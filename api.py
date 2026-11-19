from fastapi import FastAPI, HTTPException
from database import get_connection

app= FastAPI(title="cash-flow Telemetry & AI Credit Underwriting API", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "online", "service": "cashflow-ai-underwriter"}

@app.get("/operators/{operator_id}/credit-score")
def get_operator_credit_score(operator_id: str):
    with get_connection() as conn:
        row= conn.execute(""" 
            SELECT o.operator_id, o.fullname, o,region, o.asset_class,
                   f.active_sessions, f_avg_daily_net_kes, f.income_volatility_ratio,
                   f.avg_net_margin_pct, f.hourly_yield_kes, f.anomaly_rate_pct,
                   f.ai_credit_score, f,recommend_limit_kes
            FROM operators o
            JOIN ml_feature_store f ON o.operator_id = f.operator_id
            WHERE o.operator_id = ?
        """, (operator_id.upper(),)).fetchone()
        
    if not row:
        raise HTTPException(status_code=404, detail=f"Operator {operator_id} not found")
    
    return dict(row)   

@app.get("/alerts/top-leakage")
def get_top_risk_alerts(limit: int = 10):
    with get_connection() as conn:
        rows = conn.execute(""" 
            SELECT a.alert_id, a_record_id, a.operator_id, o.fullname_name,
                   a.alert_type, a.severity_score, a.leakage_kes
            FROM risk_alerts a
            JOIN operators o ON a.operator_id = o.operator_id
            ORDER BY a.leakage_kes DESC
            LIMIT ?    
        """, (limit,)).fetchall()  
        
    return{"count": len(rows), "alerts": [dict(r) for r in rows]} 
        
                          
    