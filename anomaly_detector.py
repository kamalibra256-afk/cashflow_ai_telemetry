from config import CHANNELS, ASSET_CLASSES, FUEL_UNIT_PRICE_KES,LOW_NET_MARGIN_THRESHOLD, COST_SPIKE_VARIANCE_PCT
from database import get_connection

def run_anomaly_detection():
    """Scans telemetry_logs for platform fee overcharges, fuel burn spikes, and low-margin shifts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM risk_alerts")
        
        cursor.execute(""" 
            SELECT t.*, o.asset_class
            FROM telemetry_logs t
            JOIN operators o ON t.operator_id = o.operator_id
        """)
        rows = cursor.fetchall()
        
        alerts = []
        alert_counter = 1
        
        for r in rows:
            flags = []
            severity = 0
            leakage = 0.0
            
            gross = r["gross_inflow_kes"]
            fee = r["platform_fee_kes"]
            fuel = r["fuel_energy_cost_kes"]
            dist = r["distance_km"]
            margin = r["net_margin_pct"]
            channel = r["channel"]
            asset_class = r["asset_class"]
            
            #1 platform commission overcharge check
            expected_comm_rate = CHANNELS.get(channel, {}).get("commission_rate", 0.0)
            expected_fee = round(gross * expected_comm_rate, 2)
            if fee > expected_fee + 5.0:
                flags.append("FEE_OVERCHARGE")
                severity += 40
                leakage += round(fee - expected_fee, 2)
                
            #2 Check fuel spike
            km_per_1 = ASSET_CLASSES.get(asset_class, {}).get("expected_km_per_liter", 0.0)
            if dist > 0 and km_per_1 > 0:
                expected_fuel = (dist / km_per_1) * FUEL_UNIT_PRICE_KES
                if fuel > expected_fuel * (1 + COST_SPIKE_VARIANCE_PCT):
                    flags.append("FUEL_BURN_SPIKE")
                    severity += 35
                    leakage += round(fuel - expected_fuel, 2)
                    
            # 3. Checking low net margin shift
            if margin < LOW_NET_MARGIN_THRESHOLD:
                flags.append("LOW_NET_MARGIN")
                severity += 25
                
            if flags:
                alerts.append((
                    f"ALT-{30000 + alert_counter}",
                    r["record_id"],
                    r["operator_id"],
                    " | ".join(flags),
                    min(100, severity),
                    round(leakage, 2)
            
                ))
                alert_counter += 1
                
        cursor.executemany(""" 
            INSERT INTO risk_alerts VALUES (?, ?, ?, ?, ?, ?)              
        """, alerts)       
        conn.commit()
        
    print(f"Anomaly detection complete: Flagged {len(alerts)} risk alerts in SQLite.")
    
if __name__ == "__main__":
    run_anomaly_detection()