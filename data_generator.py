import csv
import random
from datetime import datetime, timedelta
from config import DATA_DIR, CHANNELS, ASSET_CLASSES, FUEL_UNIT_PRICE_KES

REGIONS = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"]
SESSION_WINDOWS = ["Morning_Peak", "Midday_Standard", "Evening_Rush", "Night_Shift"]
FIRST_NAMES = ["Brian", "Kevin", "Faith", "Mercy", "Dennis", "Peter", "Grace", "Samuel", "Esther", "Collins", "Sharon", "David"]
LAST_NAMES = ["Kamau", "Ochieng", "Njoroge", "Wanjiku", "Mutua", "Otieno", "Kiprop", "Chebet", "Mwangi", "Omondi"]

def generate_datasets(num_operators: int = 60, num_records: int = 3000):
    random.seed(42)
    operators = []
    asset_keys = list(ASSET_CLASSES.keys())
    
    for i in range(1, num_operators + 1):
        a_class = random.choices(asset_keys, weights=[0.40, 0.35, 0.15, 0.10])[0]
        operators.append({
            "operator_id": f"OPR-{1000 + i}",
            "full_name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            "region": random.choices(REGIONS, weights=[0.45, 0.20, 0.15, 0.10, 0.10])[0],
            "asset_class": a_class,
            "tenure_months": random.randint(2, 60),
            "kyc_verified": random.choices([True, False], weights=[0.90, 0.10])[0],
            
        })
        
    records = []
    channel_keys = list(CHANNELS.keys())
    base_date = datetime(2026, 10, 1)
    
    for j in range(1, num_records + 1):
        opr = random.choice(operators)
        a_specs = ASSET_CLASSES[opr["asset_class"]]
        chan = random.choices(channel_keys, weights=[0.32, 0.28, 0.18, 0.14, 0.08])[0]
        comm_rate = CHANNELS[chan]["commission_rate"]
        
        rec_dt = base_date + timedelta(days=random.randint(0, 45))
        window = random.choice(SESSION_WINDOWS)
        hours = round(random.uniform(3.5, 11.5,), 1)
        tasks = max(2, int(hours * random.uniform(1.5, 3.0)))
        
        if opr["asset_class"] == "Micro_Retail_Kiosk":
            distance_km = 0.0
        else:
            distance_km = round(tasks * random.uniform(4.2, 13.5), 1)
        
        peak_factor = 1.22 if "Peak" in window or "Rush" in window else 0.92
        gross_kes = round(
            (a_specs["daily_gross_benchmark"] * (hours / 8.0)) * peak_factor * random.uniform(0.88, 1.18),
            2,
        )
        
        #inject 6% fee overcharges
        actual_comm_rate = comm_rate + 0.04 if random.random()  < 0.06 else  comm_rate
        platform_fee_kes = round(gross_kes * actual_comm_rate, 2)
        
        if distance_km > 0 and a_specs["expected_km_per_liter"] > 0:
            expected_litres = distance_km / a_specs["expected_km_per_liter"]
            burn_multiplier = random.uniform(1.22, 1.45) if random.random() < 0.08 else random.uniform(0.92, 1.06)
            fuel_energy_kes = round(expected_litres * burn_multiplier * FUEL_UNIT_PRICE_KES, 2)
        else:
            fuel_energy_kes = round(gross_kes * random.uniform(0.28, 0.42), 2)
            
        ancillary_kes = round(random.uniform(150.0, 600.0), 2)
        
        records.append({
            "record_id": f"REC-{20000 + j}",
            "operator_id": opr["operator_id"],
            "channel": chan,
            "record_date": rec_dt.strftime("%Y-%m-%d"),
            "session_window": window,
            "completed_tasks": tasks,
            "distance_km": distance_km,
            "active_hours": hours,
            "gross_inflow_kes": gross_kes,
            "platform_fee_kes": platform_fee_kes,
            "fuel_energy_cost_kes": fuel_energy_kes,
            "ancillary_cost_kes": ancillary_kes,
            
        })
    
    with open(DATA_DIR / "operators.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=operators[0].keys())
        writer.writeheader()
        writer.writerows(operators)
        
    with open(DATA_DIR / "raw_telemetry.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)    
        
    print(f"Generated {len(operators)} operators and {len(records)} telemetry logs in {DATA_DIR}")


if __name__ == "__main__":
        generate_datasets()
