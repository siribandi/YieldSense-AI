import unittest
import requests
import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://127.0.0.1:8000"


class MasterMilestone4TestSuite(unittest.TestCase):
    """
    Comprehensive Milestone 4 End-to-End Test Suite.
    Validates complete system integrity, authentication durability, RBAC,
    ML predictions, AgriSense AI, database relationships, farmer records, and PDF generation.
    """

    @classmethod
    def setUpClass(cls):
        # 1. Health check
        res = requests.get(f"{BASE_URL}/api/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"

        # 2. Login as Farmer 1
        f1_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "farmer1@yieldsense.com",
            "password": "Farmer1@2026!"
        })
        assert f1_res.status_code == 200, f"Farmer 1 login failed: {f1_res.text}"
        cls.f1_token = f1_res.json()["access_token"]
        cls.f1_headers = {"Authorization": f"Bearer {cls.f1_token}"}

        # 3. Login as Farmer 2
        f2_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "farmer2@yieldsense.com",
            "password": "Farmer2@2026!"
        })
        assert f2_res.status_code == 200, f"Farmer 2 login failed: {f2_res.text}"
        cls.f2_token = f2_res.json()["access_token"]
        cls.f2_headers = {"Authorization": f"Bearer {cls.f2_token}"}

        # 4. Login as Admin 1
        a1_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin1@yieldsense.com",
            "password": "Admin1@2026!"
        })
        assert a1_res.status_code == 200, f"Admin 1 login failed: {a1_res.text}"
        cls.a1_token = a1_res.json()["access_token"]
        cls.a1_headers = {"Authorization": f"Bearer {cls.a1_token}"}

        # 5. Login as Admin 2
        a2_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin2@yieldsense.com",
            "password": "Admin2@2026!"
        })
        assert a2_res.status_code == 200, f"Admin 2 login failed: {a2_res.text}"
        cls.a2_token = a2_res.json()["access_token"]
        cls.a2_headers = {"Authorization": f"Bearer {cls.a2_token}"}

    # =========================================================================
    # 1. ROOT & HEALTH CHECK
    # =========================================================================
    def test_01_root_and_health_endpoints(self):
        root_res = requests.get(f"{BASE_URL}/")
        self.assertEqual(root_res.status_code, 200)
        data = root_res.json()
        self.assertEqual(data.get("name"), "YieldSense AI API")
        self.assertEqual(data.get("status"), "online")

        health_res = requests.get(f"{BASE_URL}/api/health")
        self.assertEqual(health_res.status_code, 200)
        self.assertEqual(health_res.json().get("status"), "healthy")
        print("[TEST PASS] 1. Root & Health check endpoints verified.")

    # =========================================================================
    # 2. AUTHENTICATION & DURABILITY
    # =========================================================================
    def test_02_authentication_and_durability(self):
        # Verify /api/auth/me works for all accounts (simulating page refresh)
        for name, headers, expected_role in [
            ("Farmer 1", self.f1_headers, "Farmer"),
            ("Farmer 2", self.f2_headers, "Farmer"),
            ("Admin 1", self.a1_headers, "Administrator"),
            ("Admin 2", self.a2_headers, "Administrator")
        ]:
            res = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
            self.assertEqual(res.status_code, 200, f"{name} /api/auth/me failed")
            user_data = res.json()
            self.assertEqual(user_data["role"], expected_role)

        # Verify invalid token rejection
        invalid_res = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": "Bearer invalid_token_12345"})
        self.assertEqual(invalid_res.status_code, 401)
        print("[TEST PASS] 2. Two distinct Admin & Farmer accounts with durable JWT verified.")

    # =========================================================================
    # 3. RBAC & PERMISSION BOUNDARIES
    # =========================================================================
    def test_03_rbac_enforcement(self):
        # Farmer must be rejected with 403 Forbidden on Admin endpoints
        farmer_admin_res = requests.get(f"{BASE_URL}/api/admin/users", headers=self.f1_headers)
        self.assertEqual(farmer_admin_res.status_code, 403, "Farmer was not blocked from /api/admin/users")

        farmer_report_res = requests.get(f"{BASE_URL}/api/admin/farmers/report", headers=self.f1_headers)
        self.assertEqual(farmer_report_res.status_code, 403, "Farmer was not blocked from /api/admin/farmers/report")

        farmer_stats_res = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.f1_headers)
        self.assertEqual(farmer_stats_res.status_code, 403, "Farmer was not blocked from /api/admin/stats")

        # Admin must have full access
        admin_res = requests.get(f"{BASE_URL}/api/admin/users", headers=self.a1_headers)
        self.assertEqual(admin_res.status_code, 200)
        self.assertIsInstance(admin_res.json(), list)

        admin_stats = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.a1_headers)
        self.assertEqual(admin_stats.status_code, 200)
        print("[TEST PASS] 3. RBAC 403 Forbidden enforcement verified across protected routes.")

    # =========================================================================
    # 4. FARM & CROP MANAGEMENT
    # =========================================================================
    def test_04_farm_and_crop_management(self):
        # Fetch farms for Farmer 1
        farms_res = requests.get(f"{BASE_URL}/api/farms", headers=self.f1_headers)
        self.assertEqual(farms_res.status_code, 200)
        farms = farms_res.json()
        self.assertTrue(len(farms) >= 1)

        # Create new farm
        new_farm_payload = {
            "farm_name": "Milestone4 Test Farm",
            "location": "Amritsar, Punjab",
            "area": 12.0,
            "soil_type": "Loamy"
        }
        create_farm_res = requests.post(f"{BASE_URL}/api/farms", json=new_farm_payload, headers=self.f1_headers)
        self.assertEqual(create_farm_res.status_code, 200)
        created_farm = create_farm_res.json()
        farm_id = created_farm["id"]

        # Add crop to the farm
        crop_payload = {
            "farm_id": farm_id,
            "crop_name": "Wheat",
            "season": "Rabi",
            "sowing_date": "2026-11-15",
            "harvest_date": "2027-04-10",
            "historical_yield": 2400.0
        }
        crop_res = requests.post(f"{BASE_URL}/api/crops", json=crop_payload, headers=self.f1_headers)
        self.assertEqual(crop_res.status_code, 200)
        print("[TEST PASS] 4. Farm & Crop management CRUD workflows verified.")

    # =========================================================================
    # 5. ML MODEL & PREDICTION ENGINE
    # =========================================================================
    def test_05_ml_prediction_engine(self):
        # 1. Model Info
        model_info_res = requests.get(f"{BASE_URL}/api/ml/model-info", headers=self.f1_headers)
        self.assertEqual(model_info_res.status_code, 200)
        info = model_info_res.json()
        self.assertEqual(info["best_model_name"], "LinearRegression")
        self.assertEqual(info["model_version"], "2.0.0")
        self.assertEqual(info["dataset_size"], 1500)

        # 2. Prediction across valid agricultural inputs
        pred_payload = {
            "State": "Punjab",
            "Crop": "Wheat",
            "Soil_Type": "Loamy",
            "Fertilizer": "Urea",
            "N": 120.0,
            "P": 60.0,
            "K": 40.0,
            "Rainfall_mm": 180.0,
            "Temperature_C": 22.0,
            "Soil_pH": 6.8,
            "Year": 2026
        }
        pred_res = requests.post(f"{BASE_URL}/api/predict/yield", json=pred_payload, headers=self.f1_headers)
        self.assertEqual(pred_res.status_code, 200)
        p_data = pred_res.json()
        self.assertGreater(p_data["predicted_yield_kg_per_acre"], 0)
        self.assertIn("productivity_category", p_data)

        # 3. Invalid inputs properly caught
        invalid_payload = pred_payload.copy()
        invalid_payload["N"] = -50.0  # Invalid negative
        inv_res = requests.post(f"{BASE_URL}/api/predict/yield", json=invalid_payload, headers=self.f1_headers)
        self.assertEqual(inv_res.status_code, 422)
        print("[TEST PASS] 5. ML Model loading, inference, and input validation verified.")

    # =========================================================================
    # 6. PREDICTION HISTORY CRUD
    # =========================================================================
    def test_06_prediction_history_crud(self):
        history_res = requests.get(f"{BASE_URL}/api/predictions", headers=self.f1_headers)
        self.assertEqual(history_res.status_code, 200)
        history = history_res.json()
        self.assertIsInstance(history, list)
        self.assertTrue(len(history) >= 1)
        print(f"[TEST PASS] 6. Prediction history retrieval verified ({len(history)} records).")

    # =========================================================================
    # 7. AGRICULTURAL ANALYTICS & SYSTEM STATS
    # =========================================================================
    def test_07_analytics_and_insights(self):
        # Farmer Analytics
        f_analytics_res = requests.get(f"{BASE_URL}/api/analytics/farmer", headers=self.f1_headers)
        self.assertEqual(f_analytics_res.status_code, 200)

        # System Analytics
        s_analytics_res = requests.get(f"{BASE_URL}/api/analytics/system", headers=self.f1_headers)
        self.assertEqual(s_analytics_res.status_code, 200)
        self.assertGreater(s_analytics_res.json()["total_records_analyzed"], 1000)

        # Risk & Insights
        risk_payload = {
            "Crop": "Wheat",
            "Soil_Type": "Loamy",
            "Fertilizer": "Urea",
            "N": 120.0,
            "P": 60.0,
            "K": 40.0,
            "Rainfall_mm": 180.0,
            "Temperature_C": 22.0,
            "Soil_pH": 6.8
        }
        risk_res = requests.post(f"{BASE_URL}/api/insights/analyze", json=risk_payload, headers=self.f1_headers)
        self.assertEqual(risk_res.status_code, 200)
        r_data = risk_res.json()
        self.assertIn("overall_risk_level", r_data)
        print("[TEST PASS] 7. Agricultural Analytics & Risk Insight Engine verified.")

    # =========================================================================
    # 8. AGRISENSE AI CHATBOT ENGINE
    # =========================================================================
    def test_08_agrisense_ai_chatbot(self):
        test_queries = [
            ("What is Python?", "programming"),
            ("Explain photosynthesis.", "science"),
            ("What is the best soil for rice?", "soil_health"),
            ("which crop kis good for my form", "personalized_crop_advisory"),
            ("tell me about my form", "personalized_farms"),
            ("Write a Java program for factorial", "programming"),
            ("Explain quantum computing", "general_knowledge")
        ]

        for query, expected_cat in test_queries:
            chat_res = requests.post(f"{BASE_URL}/api/chat", json={"message": query}, headers=self.f1_headers)
            self.assertEqual(chat_res.status_code, 200, f"Chatbot query failed: {query}")
            c_data = chat_res.json()
            self.assertTrue(len(c_data.get("reply", "")) > 50, f"Short reply for: {query}")
            self.assertNotIn("I am ready to help you across multiple domains", c_data["reply"])

        # Check chat history persistence
        chat_hist_res = requests.get(f"{BASE_URL}/api/chat/history", headers=self.f1_headers)
        self.assertEqual(chat_hist_res.status_code, 200)
        self.assertTrue(len(chat_hist_res.json()) >= len(test_queries))
        print("[TEST PASS] 8. AgriSense AI multi-domain & personalized intelligence verified.")

    # =========================================================================
    # 9. ADMIN FARMER RECORDS & PDF REPORT GENERATION
    # =========================================================================
    def test_09_farmer_records_and_pdf_report(self):
        # 1. Admin Farmer Records
        farmers_res = requests.get(f"{BASE_URL}/api/admin/users", headers=self.a1_headers)
        self.assertEqual(farmers_res.status_code, 200)
        farmers = farmers_res.json()
        self.assertTrue(len(farmers) >= 2)

        # 2. PDF Report Generation
        report_res = requests.get(f"{BASE_URL}/api/admin/farmers/report", headers=self.a1_headers)
        self.assertEqual(report_res.status_code, 200)
        self.assertEqual(report_res.headers.get("Content-Type"), "application/pdf")
        self.assertIn("YieldSense_AI_Farmer_Report.pdf", report_res.headers.get("Content-Disposition", ""))
        self.assertTrue(report_res.content.startswith(b"%PDF-"), "Generated report is not a valid PDF")
        self.assertGreater(len(report_res.content), 2000, "PDF size is too small")
        print(f"[TEST PASS] 9. Admin Farmer records & PDF Report verified ({len(report_res.content):,} bytes).")


if __name__ == "__main__":
    unittest.main(verbosity=2)
