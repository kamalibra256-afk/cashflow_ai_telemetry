# Real-Time Cash-Flow Telemetry & AI Underwriting Portal

An end-to-end python, SQLite, Scikit-learn, FastAPI, and Streamlit pipeline that captures high-frequency gig and micro-enterprise cash-flow telemetry, detects fee overcharges and fuel burn anomalies, engine behavioral financial features, and trains random forest underwriting model to predict 0-100 AI creditworthiness scores and working-capital-limits (KES).

## Quickstart
1. Install dependencies:
   '''bash
   pip install -r requirement.txt
   '''
2. Run the full data & ML pipeline:
   '''bash
   python main.py
   '''
3. Run automated unit tests:
   '''bash
   python test_pipeline.py
   '''
4. Launch the stramlit web portal:
   '''bash
   streamlit run app.py
   '''
5. Launch the FastAPI credit scoring endpoint:
   '''bash
   uvicorn api.app --reload   
   '''