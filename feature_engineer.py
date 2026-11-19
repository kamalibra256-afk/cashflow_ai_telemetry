import math
from database import get_connection
from config import MIN_ACTIVE_DAYS_FOR_CREDIT

def build_feature_store():
    """Engineers behavioral & cash-flow ML features per operator and stores them inSQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ml_feature_store")
        
        cursor.execute(""" 
            SELECT o.operator_id, o.tenure_months, o.kyc_verified,
                   COUNT(T.record_id) AS session_count,
                   AVG(t.net_profit_kes) AS avg_net_kes,
                   AVG(t.net_margin_pct) AS avg_margin_pct,
                   SUM(t.net_profit_kes) / NULLIF(SUM(t.active_hours), 0) AS hourly_yield
            From operators o
            LEFT JOIN telemetry_logs t ON o.operator_id = t.operator_id
            GROUP BY o.operator_id 
        """)
        operator_stats = cursor.fetchall()
        
        feature_rows = []
        for row in operator_stats:
            opr_id = row["operator_id"]
            sessions = row["session_count"] or 0
            avg_net = row["avg_net_kes"] or 0.0
            avg_margin = row["avg_margin_pct"] or 0.0
            hourly_yield = row["hourly_yield"] or 0.0
            
            #fetch individual session net profits
            cursor.execute("SELECT net_profit_kes FROM telemetry_logs WHERE operator_id = ?", (opr_id,))
            profits = [r["net_profit_kes"] for r in cursor.fetchall()]
            
            if len(profits) > 1 and avg_net > 0:
                variance = sum((p-avg_net) ** 2 for p in profits) / len(profits)
                std_dev = math.sqrt(variance)
                volatility_ratio = round(std_dev / avg_net, 4)
                
            else:
                volatility_ratio = 1.0
                
            # Calculate anomaly rate per operator
            cursor.execute("SELECT COUNT(*) AS alert_cnt FROM risk_alerts WHERE operator_id = ?", (opr_id,))
            alert_cnt = cursor.fetchone()["alert_cnt"] or 0
            anomaly_rate = round((alert_cnt / sessions) * 100, 2) if sessions > 0 else 0.0
            
            #computing baseline target
            consistency_pts = max(0.0, 35.0 * (1.0 - min(volatility_ratio, 1.0 )))
            margin_pts = min(30.0, max(0.0, avg_margin * 50.0))
            activity_pts = 20.0 if sessions >=MIN_ACTIVE_DAYS_FOR_CREDIT else (sessions / MIN_ACTIVE_DAYS_FOR_CREDIT) * 20.0
            
            clean_pts = max(0.0, 15.0 - (anomaly_rate * 0.5))
            kyc_bonus = 5.0 if row["kyc_verified"] == 1 else -10.0
            
            target_score = round(min(100.0, max(0.0, consistency_pts + margin_pts + activity_pts + clean_pts + kyc_bonus)), 2)
            rec_limit_kes = round(max(0.0, avg_net * 12* (target_score / 100.0)), 2) if sessions >= MIN_ACTIVE_DAYS_FOR_CREDIT else 0.0
            
            feature_rows.append((
                 opr_id,
                 sessions,
                 round(avg_net, 2),
                 volatility_ratio,
                 round(avg_margin, 4),
                 round(hourly_yield, 2),
                 anomaly_rate,
                 target_score,
                 rec_limit_kes,
            ))   
            
        cursor.executemany(""" 
            INSERT INTO ml_feature_store VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, feature_rows)
        conn.commit()
        
    print(f"Engineered ML feature vectors for {len(feature_rows)} operators in ml_feature_store.")
      
if __name__ == "__main__":
    build_feature_store()         
                           
        