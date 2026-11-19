import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from database import get_connection

def train_and_score_credit_model():
    """Trains a Random Forest model on engineered cash-flow features and updates AI credit scores."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.operator_id, f.active_sessions, f.avg_daily_net_kes,
                   f.income_volatility_ratio, f.avg_net_margin_pct,
                   f.hourly_yield_kes, f.anomaly_rate_pct,
                   o.tenure_months, o.kyc_verified, f.ai_credit_score
            FROM ml_feature_store f
            JOIN operators o ON f.operator_id = o.operator_id
        """)
        rows = cursor.fetchall()
        
        if len(rows) < 10:
            print("Not enough operator records to train ML model.")
            return
        
        X = np.array([
            [
                r["active_sessions"],
                r["avg_daily_net_kes"],
                r["income_volatility_ratio"],
                r["avg_net_margin_pct"],
                r["hourly_yield_kes"],
                r["anomaly_rate_pct"],
                r["tenure_months"],
                r["kyc_verified"],
            ]
            for r in rows
        ])
        y = np.array([r["ai_credit_score"] for r in rows])
        
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(x_train, y_train)
        
        preds_test = model.predict(x_test)
        mae = round(mean_absolute_error(y_test, preds_test), 2)
        r2 = round(r2_score(y_test, preds_test), 3)
        
        all_preds = model.predict(X)
        updates = []
        for idx, r in enumerate(rows):
            ml_score = round(float(np.clip(all_preds[idx], 0.0, 100.0)), 2)
            rec_limit = round(r["avg_daily_net_kes"] * 12 * (ml_score / 100.0), 2) if r["active_sessions"] >= 10 else 0.0
            updates.append((ml_score, rec_limit, r["operator_id"]))
            
        cursor.executemany(""" 
            UPDATE ml_feature_store
            SET ai_credit_score = ?, recommended_limit_kes = ?
            WHERE operator_id = ?
        """, updates)
        conn.commit()
        
    print(f"ML Underwriter Trained | Test MAE: {mae} pts | R2 Score: {r2}")
    
if __name__ == "__main__":
    train_and_score_credit_model()