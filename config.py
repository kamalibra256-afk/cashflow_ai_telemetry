from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "ai_exports"
DB_PATH = DATA_DIR / "telemetry_store.db"

DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

#digital platforms and trade channels
CHANNELS = {
    "Ride_Hailing_A": {"commission_rate": 0.18, "sector": "Mobility"},
    "Ride_Hailing_B": {"commission_rate": 0.18, "sector": "Mobility"},
    "Delivery_Network": {"commission_rate": 0.02, "sector": "Retail_POS"},
    "Delivery_Merchant": {"commission_rate": 0.02, "sector": "Retail_POS"},
    "B2B_Contract": {"commission_rate": 0.00, "sector": "Commercial_Freight"}
}

# operator Asset classes (Expected Operating Efficiency & Daily gross Benchmark)
ASSET_CLASSES = {
    "Two_Wheeler": {"expected_km_per_liter": 38.0, "daily_gross_benchmark":2400.0},
    "Compact_Sedan": {"expected_km_per_liter": 14.5, "daily_gross_benchmark":4800.0},
    "Light_Commercial_Van": {"expected_km_per_liter": 10.5, "daily_gross_benchmark":7500.0},
    "Micro_Retail_Kiosk": {"expected_km_per_liter": 0.0, "daily_gross_benchmark":6000.0},
}

# fuel, cost & AI underwriting Threshold
FUEL_UNIT_PRICE_KES = 180.50
LOW_NET_MARGIN_THRESHOLD = 0.42   #flag if net margin drops by 42%
COST_SPIKE_VARIANCE_PCT = 0.15    # flags if fuel exceed > 15%
MIN_ACTIVE_DAYS_FOR_CREDIT = 10   # Minimum recorded shifts for credit elegibility

    