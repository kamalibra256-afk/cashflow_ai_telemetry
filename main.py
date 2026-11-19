from data_generator import generate_datasets
from database import init_db
from ingestion import ingest_all
from anomaly_detector import run_anomaly_detection
from feature_engineer import build_feature_store
from ml_underwriter import train_and_score_credit_model
from exporter import export_ai_datasets

def run_full_pipeline():
    print("=== Starting Cash-Flow Telemetry & AI Underwriting Pipeline ===")
    generate_datasets()
    init_db()
    ingest_all()
    run_anomaly_detection()
    build_feature_store()
    train_and_score_credit_model()
    export_ai_datasets()
    print("=== Pipeline Completed Successfully ===")
    
if __name__ == "__main__":
    run_full_pipeline()