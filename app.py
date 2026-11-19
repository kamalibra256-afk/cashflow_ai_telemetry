import streamlit as st 
import pandas as pd
from datetime import date
from config import CHANNELS, ASSET_CLASSES, FUEL_UNIT_PRICE_KES, LOW_NET_MARGIN_THRESHOLD, COST_SPIKE_VARIANCE_PCT
from database import get_connection
from feature_engineer import build_feature_store
from ml_underwriter import train_and_score_credit_model
from exporter import export_ai_datasets
from pathlib import Path
from config import DB_PATH
from main import run_full_pipeline

if not path{DB_PATH}.exists():
    run_full_pipeline()

st.set_page_config(page_title= "AI Cash-Flow Telemetry & Underwriting Portal", layout="wide")
st.title("📊 Real-Time Cash-Flow Telemetry & AI Undewriting Portal")
st.caption("High-Frequency Behavioral Recording, Anomaly Detection & ML Credit Scoring Engine")

# sidebar
st.sidebar.header("+ Record Live Telemetry session")
with get_connection() as conn:
    operators_df = pd.read_sql_query("SELECT operator_id, full_name, region, asset_class FROM operators", conn)
    
opr_map = {f"{row['operator_id']} - {row['full_name']} ({row['asset_class']})": row for _, row in operators_df.iterrows()}
selected_opr_label = st.sidebar.selectbox("Select Operator", list(opr_map.keys()))
selected_opr = opr_map[selected_opr_label]

channel = st.sidebar.selectbox("Channel", list(CHANNELS.keys()))
session_window = st.sidebar.selectbox("Session Window", ["Morning_Peak", "Midday_Standard", "Evening_Rush", "Night_Shift"])
rec_date = st.sidebar.date_input("Session Date", value=date.today())
completed_tasks = st.sidebar.number_input("Completed Tasks / Trips", min_value=1, max_value=100, value=12)
distance_km = st.sidebar.number_input("Distance Covered (km)", min_value=0.0, max_value=1000.0, value=85.0)
active_hours = st.sidebar.number_input("Active Hours", min_value=0.5, max_value=24.0, value=8.0)
gross_inflow = st.sidebar.number_input("Gross Inflow (KES)", min_value=100.0, max_value=200000.0, value=4500.0)
platform_fee = st.sidebar.number_input(
    
    "Platform Fee Charged (KES)",
    min_value=0.0,
    max_value=50000.0,
    value=round(gross_inflow * CHANNELS[channel]["commission_rate"], 2),
)
fuel_cost = st.sidebar.number_input("Fuel / Energy Cost (KES)", min_value=0.0, max_value=50000.0, value=1100.0)
ancillary_cost =st.sidebar.number_input("Ancillary / Data / Maintenance (KES)", min_value=0.0, max_value=20000.0, value=250.0)

if st.sidebar.button(" Save Telemetry & Retrain AI Model", width='stretch'):
    net_profit = round(gross_inflow - (platform_fee + fuel_cost + ancillary_cost), 2)
    net_margin = round(net_profit / gross_inflow, 4) if gross_inflow > 0 else 0.0
    
    with get_connection() as conn:
        cursor = conn.cursor()
        count = cursor.execute("SELECT COUNT(*) FROM telemetry_logs").fetchone()[0]
        new_rec_id = f"REC-{20001 + count}"
        
        cursor.execute("""
            INSERT INTO telemetry_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_rec_id,selected_opr["operator_id"], channel, rec_date.strftime("%Y-%m-%d"),
            session_window, completed_tasks, distance_km, active_hours,
            gross_inflow, platform_fee, fuel_cost, ancillary_cost, net_profit, net_margin
        ))

        #Run live anomaly check
        flags, severity, leakage = [], 0, 0.0
        exp_fee = round(gross_inflow * CHANNELS[channel]["commission_rate"], 2)
        if platform_fee > exp_fee + 5.0:
            flags.append("FEE_OVERCHARGE")
            severity += 40
            leakage += round(platform_fee - exp_fee, 2)
            
        km_per_1 = ASSET_CLASSES[selected_opr["asset_class"]]["expected_km_per_liter"]
        if distance_km >0 and km_per_1 > 0:
            exp_fuel = (distance_km / km_per_1) * FUEL_UNIT_PRICE_KES
            if fuel_cost > exp_fuel * (1 + COST_SPIKE_VARIANCE_PCT):
                flags.append("FUEL_BURN_SPIKE")
                severity += 35
                leakage += 25
                
            if flags:
                alt_count = cursor.execute("SELECT COUNT(*) FROM risk_alerts").fetchone()[0]
                cursor.execute("""
                    INSERT INTO risk_alerts VALUES (?, ?, ?, ?, ?, ?)
                """, (F"ALT-{30001 + alt_count}", new_rec_id, selected_opr["operator_id"], " | ".join(flags), min(100, severity), round(leakage, 2)))
                
            conn.commit()  
            
        build_feature_store()  
        train_and_score_credit_model()
        export_ai_datasets()
        st.sidebar.success(f"Recorded {new_rec_id}! Net Profit: KES {net_profit:,.2f}. AI Model Updated.")
        
# Main Dashboard: Load Live data from SQLite
with get_connection() as conn:
    features_df = pd.read_sql_query("""
        SELECT o.operator_id, o.full_name, o.region, o.asset_class, o.tenure_months, o.kyc_verified,
            f.active_sessions, f.avg_daily_net_kes, f.income_volatility_ratio,
            f.avg_net_margin_pct, f.hourly_yield_kes, f.anomaly_rate_pct,
            f.ai_credit_score, f.recommended_limit_kes
        FROM operators o
        JOIN ml_feature_store f ON o.operator_id = f.operator_id
        ORDER BY F.ai_credit_score DESC
    """, conn)
    
    alerts_df = pd.read_sql_query("""
        SELECT a.alert_id, a.record_id, o.full_name, o.region, a.alert_type, a.severity_score, a.leakage_kes
        FROM risk_alerts a
        JOIN operators o ON a.operator_id = o.operator_id
        ORDER BY a.severity_score DESC, a.leakage_kes DESC
    """, conn)
    
    telemetry_df = pd.read_sql_query("SELECT * FROM telemetry_logs", conn)
    
#  Top API cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Telemetry logs", f"{len(telemetry_df):,}")
col2.metric("Portfolio Gross Inflow", f"KES {telemetry_df['gross_inflow_kes'].sum():,.0f}")
col3.metric("Avg AI Credit Score", f"{features_df['ai_credit_score'].mean():.1f} / 100")
col4.metric("Detected Cost Leakage", f"KES {alerts_df['leakage_kes'].sum():,.0f}")

tab1, tab2, tab3 =st.tabs(["AI Credit Underwriting", "Anomaly & Leakage Audit", "ML Feature Store Export"])

with tab1:
    st.subheader("Operator AI Credit Scores & Working-Capital Limits")
    region_filter = st.multiselect("Filter by Region", options=features_df["region"].unique(), default=list(features_df["region"].unique()))
    filtered_features = features_df[features_df["region"].isin(region_filter)]
    
    st.bar_chart(filtered_features.set_index("full_name")["ai_credit_score"].head(15))
    st.dataframe(filtered_features, width='stretch')
with tab2:
    st.subheader("Flagged Fee Overcharges, Fuel Spikes & Low-Margin Shifts") 
    st.dataframe(alerts_df, width='stretch')   
    
with tab3:
    st.subheader("Labeled AL Training Dataset (Ready for External ML Pipelines)")
    st.dataframe(features_df, width='stretch')
    csv_bytes = features_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download AI feature Store (CSV)", data=csv_bytes, file_name="ai_ml_training_features.csv", mime="text/csv")