import sqlite3
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the 4-table SQLite relational telemetry & ML feature store."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS operators (
                operator_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                region TEXT NOT NULL,
                asset_class TEXT NOT NULL,
                tenure_months INTEGER NOT NULL,
                kyc_verified INTEGER NOT NULL
            )          
        """)
        
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS telemetry_logs (
                record_id TEXT PRIMARY KEY,
                operator_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                record_date TEXT NOT NULL,
                session_window TEXT NOT NULL,
                completed_tasks INTEGER NOT NULL,
                distance_km REAL NOT NULL,
                active_hours REAL NOT NULL,
                gross_inflow_kes REAL NOT NULL,
                platform_fee_kes REAL NOT NULL,
                fuel_energy_cost_kes REAL NOT NULL,
                ancillary_cost_kes REAL NOT NULL,
                net_profit_kes REAL NOT NULL,
                net_margin_pct REAL NOT NULL,
                FOREIGN KEY (operator_id) REFERENCES operators(operator_id)
            )           
        """)           
                       
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_alerts (
                alert_id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL,
                operator_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity_score INTEGER NOT NULL,
                leakage_kes REAL NOT NULL,
                FOREIGN KEY (record_id) REFERENCES telemetry_logs(record_id)
            )          
                       
        """)
        
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS ml_feature_store (
                operator_id TEXT PRIMARY KEY,
                active_sessions INTEGER NOT NULL,
                avg_daily_net_kes REAL NOT NULL,
                income_volatility_ratio REAL NOT NULL,
                avg_net_margin_pct REAL NOT NULL,
                hourly_yield_kes REAL NOT NULL,
                anomaly_rate_pct REAL NOT NULL,
                ai_credit_score REAL NOT NULL,
                recommended_limit_kes REAL NOT NULL,
                FOREIGN KEY (operator_id) REFERENCES operators(operator_id)
            )           
        """)
        
        conn.commit()   
    print(f"Database initialized successfully at {DB_PATH}")
    

if __name__ == "__main__":
    init_db()   
                       
                                     
                       
                       
                                    
                       
                       