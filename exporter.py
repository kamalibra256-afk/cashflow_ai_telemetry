import csv
import json
from config import OUTPUT_DIR
from database import get_connection

def export_ai_datasets():
    """Exports labeled ML training features (CSV + JSON) and anomaly audit logs."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(""" 
            SELECT o.operator_id, o.full_name, o.region, o.asset_class,
                   o.tenure_months, o.kyc_verified,
                   f.active_sessions, f.avg_daily_net_kes,
                   f.income_volatility_ratio, f.avg_net_margin_pct,
                   f.hourly_yield_kes, f.anomaly_rate_pct,
                   f.ai_credit_score, f.recommended_limit_kes
            FROM operators o
            JOIN ml_feature_store f ON o.operator_id = f.operator_id
            ORDER BY f.ai_credit_score DESC
        """)       
        ml_rows = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute(""" 
            SELECT a.alert_id, a.record_id, a.operator_id, o.full_name, o.region,
                   a.alert_type, a.severity_score, a.leakage_kes
            FROM risk_alerts a
            JOIN operators o ON a.operator_id = o.operator_id
            ORDER BY a.severity_score DESC, a.leakage_kes DESC
        """)
        alert_rows = [dict(row) for row in cursor.fetchall()]
        
    if ml_rows:
        csv_path = OUTPUT_DIR / "ai_ml_training_features.csv"
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer= csv.DictWriter(f, fieldnames=ml_rows[0].keys())
            writer.writeheader()
            writer.writerows(ml_rows)
            
        json_path = OUTPUT_DIR / "ai_ml_training_features.json"
        with open(json_path, mode="w", encoding="utf-8") as f:
            json.dump(ml_rows, f, indent=2)
            
            
    if alert_rows:
        alerts_path = OUTPUT_DIR / "risk_alerts_audit.csv"
        with open(alerts_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=alert_rows[0].keys())
            writer.writeheader()
            writer.writerows(alert_rows)
            
    print(f"exported {len(ml_rows)} ML feature profiles and {len(alert_rows)}")
    
if __name__ == "__main__":
    export_ai_datasets()
    
            
        
                    