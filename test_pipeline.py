import unittest
from database import get_connection
from main import run_full_pipeline

class TestCashflowTelemetryPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_full_pipeline()  
        
    def test_database_populated(self):
        with get_connection() as conn:
            opr_count = conn.execute("SELECT COUNT(*) FROM operators").fetchone()[0]
            tel_count = conn.execute("SELECT COUNT(*) FROM telemetry_logs").fetchone()[0]
            self.assertEqual(opr_count, 60)
            self.assertGreaterEqual(tel_count, 3000)
            
    def test_ai_credit_scores_bounded(self):
        with get_connection() as conn:
            scores = [r["ai_credit_score"] for r in conn.execute("SELECT ai_credit_score FROM ml_feature_store").fetchall()]
            self.assertTrue(len(scores) > 0)
            for s in scores:
                self.assertGreaterEqual(s, 0.0)
                self.assertLessEqual(s, 100.0)
                
    def test_anomaly_detection_active(self):
        with get_connection() as conn:
            alert_count = conn.execute("SELECT COUNT(*) FROM risk_alerts").fetchone()[0]
            self.assertGreater(alert_count, 0)
            
if __name__ == "__main__":
    unittest.main()