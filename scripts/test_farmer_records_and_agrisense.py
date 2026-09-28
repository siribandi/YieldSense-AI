import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.config import SessionLocal
from backend.app.db.models import User, Farm, Crop, Prediction

client = TestClient(app)

class TestFarmerRecordsAndAgriSense(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        
        # 1. Register/Login Admin
        cls.admin_email = "admin.audit@yieldsense.ai"
        cls.admin_pass = "AdminSecPass123!"
        client.post("/api/auth/register", json={
            "name": "Platform Administrator",
            "email": cls.admin_email,
            "password": cls.admin_pass,
            "role": "Administrator"
        })
        res_adm = client.post("/api/auth/login", json={"email": cls.admin_email, "password": cls.admin_pass})
        cls.admin_token = res_adm.json()["access_token"]
        cls.headers_adm = {"Authorization": f"Bearer {cls.admin_token}"}

        # 2. Register/Login Farmer 1
        cls.farmer_email = "farmer.ramesh.audit@yieldsense.ai"
        cls.farmer_pass = "FarmerPass123!"
        client.post("/api/auth/register", json={
            "name": "Ramesh Patel",
            "email": cls.farmer_email,
            "password": cls.farmer_pass,
            "role": "Farmer"
        })
        res_f1 = client.post("/api/auth/login", json={"email": cls.farmer_email, "password": cls.farmer_pass})
        cls.farmer_token = res_f1.json()["access_token"]
        cls.headers_f1 = {"Authorization": f"Bearer {cls.farmer_token}"}

        # Seed 1 Farm, 1 Crop, 1 Prediction for Farmer 1
        res_farm = client.post("/api/farms", json={
            "farm_name": "Sunrise Organic Acres",
            "location": "Nashik, Maharashtra",
            "area": 5.5,
            "soil_type": "Black Soil"
        }, headers=cls.headers_f1)
        cls.farm_id = res_farm.json()["id"]

        client.post("/api/crops", json={
            "farm_id": cls.farm_id,
            "crop_name": "Soybean",
            "season": "Kharif",
            "sowing_date": "2026-06-15",
            "harvest_date": "2026-10-20"
        }, headers=cls.headers_f1)

        client.post("/api/predictions", json={
            "farm_id": cls.farm_id,
            "State": "Maharashtra",
            "Crop": "Soybean",
            "Soil_Type": "Black",
            "Fertilizer": "DAP",
            "N": 35.0,
            "P": 65.0,
            "K": 45.0,
            "Rainfall_mm": 145.0,
            "Temperature_C": 28.5,
            "Soil_pH": 6.7,
            "Year": 2026
        }, headers=cls.headers_f1)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # -------------------------------------------------------------
    # 1. Admin Farmer Records Verification
    # -------------------------------------------------------------
    def test_01_admin_farmer_records_list(self):
        res = client.get("/api/admin/users", headers=self.headers_adm)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)

        # Check farmer record fields
        farmer_rec = next((u for u in data if u["email"] == self.farmer_email), None)
        self.assertIsNotNone(farmer_rec)
        self.assertEqual(farmer_rec["name"], "Ramesh Patel")
        self.assertEqual(farmer_rec["role"], "Farmer")
        self.assertGreaterEqual(farmer_rec["farms_count"], 1)
        self.assertGreaterEqual(farmer_rec["crops_count"], 1)
        self.assertGreaterEqual(farmer_rec["predictions_count"], 1)
        self.assertEqual(farmer_rec["status"], "Active")
        self.assertIn("Forecast", farmer_rec["recent_activity"])
        print(f"[TEST PASS] 1. Farmer Records: Successfully loaded {len(data)} users from PostgreSQL.")

    # -------------------------------------------------------------
    # 2. PDF Download Report Verification
    # -------------------------------------------------------------
    def test_02_admin_download_pdf_report(self):
        res = client.get("/api/admin/farmers/report/pdf", headers=self.headers_adm)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "application/pdf")
        self.assertIn("attachment; filename=", res.headers.get("content-disposition", ""))
        self.assertGreater(len(res.content), 2000)
        self.assertTrue(res.content.startswith(b"%PDF"))
        print(f"[TEST PASS] 2. Download Report: Dynamic PDF report generated ({len(res.content):,} bytes).")

    # -------------------------------------------------------------
    # 3. RBAC Enforcement (Farmer cannot access admin endpoints)
    # -------------------------------------------------------------
    def test_03_farmer_cannot_access_admin_records_or_pdf(self):
        res_users = client.get("/api/admin/users", headers=self.headers_f1)
        self.assertEqual(res_users.status_code, 403, "Farmer should be blocked from /api/admin/users")

        res_pdf = client.get("/api/admin/farmers/report/pdf", headers=self.headers_f1)
        self.assertEqual(res_pdf.status_code, 403, "Farmer should be blocked from /api/admin/farmers/report/pdf")
        print("[TEST PASS] 3. RBAC Protection: Farmer access to admin reports blocked with HTTP 403.")

    # -------------------------------------------------------------
    # 4. AgriSense AI Natural Language Questions (Domain Variety)
    # -------------------------------------------------------------
    def test_04_agrisense_crop_and_soil_questions(self):
        # A. Crop cultivation question with natural phrasing
        res_crop = client.post("/api/chat", json={"message": "Could you tell me how to grow wheat and what is the best sowing time?"})
        self.assertEqual(res_crop.status_code, 200)
        reply = res_crop.json()["reply"]
        self.assertIn("Wheat", reply)
        self.assertIn("Rabi", reply)
        self.assertIn("Seed Rate", reply)

        # B. Soil pH & Acidity question
        res_soil = client.post("/api/chat", json={"message": "My soil pH is 5.2 and acidic. What treatment do you recommend?"})
        self.assertEqual(res_soil.status_code, 200)
        reply_soil = res_soil.json()["reply"]
        self.assertIn("Lime", reply_soil)
        self.assertIn("Calcium Carbonate", reply_soil)

        # C. Fertilizer schedule
        res_fert = client.post("/api/chat", json={"message": "When should I apply DAP and Urea for my cotton crop?"})
        self.assertEqual(res_fert.status_code, 200)
        reply_fert = res_fert.json()["reply"]
        self.assertIn("Cotton", reply_fert)
        self.assertIn("DAP", reply_fert)

        # D. Weather and heat stress
        res_weather = client.post("/api/chat", json={"message": "How do extreme heat and temperatures above 35 degrees impact wheat grain filling?"})
        self.assertEqual(res_weather.status_code, 200)
        reply_w = res_weather.json()["reply"]
        self.assertIn("Heat Stress", reply_w)

        # E. Crop disease & pests
        res_dis = client.post("/api/chat", json={"message": "What causes Yellow Mosaic Virus in soybean and how to prevent it?"})
        self.assertEqual(res_dis.status_code, 200)
        reply_dis = res_dis.json()["reply"]
        self.assertIn("Soybean", reply_dis)
        self.assertIn("Mosaic", reply_dis)
        print("[TEST PASS] 4. AgriSense AI: Answered natural-language questions across Crops, Soil, Fertilizers, Weather, and Diseases.")

    # -------------------------------------------------------------
    # 5. AgriSense AI Out-of-Scope Redirection
    # -------------------------------------------------------------
    def test_05_agrisense_out_of_scope_redirection(self):
        res_off = client.post("/api/chat", json={"message": "Who is the president of France and what is the capital?"})
        self.assertEqual(res_off.status_code, 200)
        reply_off = res_off.json()["reply"]
        self.assertEqual(res_off.json()["category"], "out_of_scope")
        self.assertIn("agricultural intelligence assistant", reply_off)
        self.assertIn("outside agriculture", reply_off)
        print("[TEST PASS] 5. AgriSense AI: Out-of-scope question politely redirected to agriculture.")

    # -------------------------------------------------------------
    # 6. AgriSense AI Personalized User Records Lookup
    # -------------------------------------------------------------
    def test_06_agrisense_personalized_data_queries(self):
        # A. Logged-in farmer asks about their farms
        res_farm = client.post("/api/chat", json={"message": "Can you show me my registered farms?"}, headers=self.headers_f1)
        self.assertEqual(res_farm.status_code, 200)
        reply_f = res_farm.json()["reply"]
        self.assertIn("Sunrise Organic Acres", reply_f)
        self.assertIn("5.5 acres", reply_f)
        self.assertIn("Black Soil", reply_f)

        # B. Logged-in farmer asks about their yield predictions
        res_pred = client.post("/api/chat", json={"message": "What is my latest crop yield prediction?"}, headers=self.headers_f1)
        self.assertEqual(res_pred.status_code, 200)
        reply_p = res_pred.json()["reply"]
        self.assertIn("Soybean", reply_p)
        self.assertIn("kg/acre", reply_p)

        # C. Unauthenticated user asks for personal data -> clearly prompts login
        res_unauth = client.post("/api/chat", json={"message": "What are my registered farms and predicted yield?"})
        self.assertEqual(res_unauth.status_code, 200)
        reply_u = res_unauth.json()["reply"]
        self.assertIn("log in", reply_u.lower())
        print("[TEST PASS] 6. AgriSense AI: Real database lookup for personal farms & predictions verified.")

    # -------------------------------------------------------------
    # 7. Regression Test: Milestone 1, 2, 3 Intact
    # -------------------------------------------------------------
    def test_07_regression_milestones_intact(self):
        # Health
        res_h = client.get("/api/health")
        self.assertEqual(res_h.status_code, 200)

        # ML Model info
        res_m = client.get("/api/ml/model-info")
        self.assertEqual(res_m.status_code, 200)
        self.assertEqual(res_m.json()["best_model_name"], "LinearRegression")

        # Yield Prediction
        res_p = client.post("/api/predict/yield", json={
            "State": "Karnataka", "Crop": "Soybean", "Soil_Type": "Loamy",
            "Fertilizer": "DAP", "N": 56, "P": 41, "K": 51,
            "Rainfall_mm": 120, "Temperature_C": 31.06, "Soil_pH": 6.82, "Year": 2024
        })
        self.assertEqual(res_p.status_code, 200)
        self.assertIn("predicted_yield_kg_per_acre", res_p.json())

        # System Analytics
        res_a = client.get("/api/analytics/system", headers=self.headers_f1)
        self.assertEqual(res_a.status_code, 200)
        print("[TEST PASS] 7. Regression: All existing prediction, analytics, model-info, and health APIs 100% functional.")

if __name__ == "__main__":
    unittest.main()
