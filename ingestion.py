import csv
from config import DATA_DIR
from database import get_connection

def ingest_all():
    """Loads operators.csv and raw_telemetry.csv into SQLite with calculated net profit & margins."""
    operators_path = DATA_DIR / "operators.csv"
    telemetry_path = DATA_DIR / "raw_telemetry.csv"
    
    with open(operators_path, mode="r", encoding="utf-8") as f:
        opr_reader = csv.DictReader(f)
        operators_data = [
            (
                row["operator_id"].strip(),
                row["full_name"].strip(),
                row["region"].strip(),
                row["asset_class"].strip(),
                int(row["tenure_months"]),
                1 if row["kyc_verified"].strip().lower() == "true" else 0,
            )
            for row in opr_reader
        ]
        
    with open(telemetry_path, mode="r", encoding="utf-8") as f:
        tel_reader = csv.DictReader(f)
        telemetry_data = []
        for row in tel_reader:
            gross = float(row["gross_inflow_kes"])
            fee = float(row["platform_fee_kes"])
            fuel = float(row["fuel_energy_cost_kes"])
            ancillary = float(row["ancillary_cost_kes"])
            
            net_profit = round(gross - (fee + fuel + ancillary), 2)
            net_margin = round(net_profit / gross, 4) if gross > 0 else 0.0
            
            telemetry_data.append((
                row["record_id"].strip(),
                row["operator_id"].strip(),
                row["channel"].strip(),
                row["record_date"].strip(),
                row["session_window"].strip(),
                int(row["completed_tasks"]),
                float(row["distance_km"]),
                float(row["active_hours"]),
                gross,
                fee,
                fuel,
                ancillary,
                net_profit,
                net_margin,
                
            ))
            
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM telemetry_logs")
        cursor.execute("DELETE FROM operators")
        
        cursor.executemany(""" 
            INSERT INTO operators VALUES (?, ?, ?, ?, ?, ?)   
        """, operators_data)
        
        cursor.executemany(""" 
            INSERT INTO telemetry_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)                     
        """, telemetry_data)
        
        conn.commit()
        
    print(f"Ingested {len(operators_data)} operators and {len(telemetry_data)} telemetry logs into SQLite.")
    
if __name__ == "__main__":
      ingest_all()