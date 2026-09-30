import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app
from backend.app.db.config import SessionLocal, Base, engine
from backend.app.db.models import User, Farm, Crop, Prediction, ChatMessage
from backend.app.db.seed import seed_initial_accounts

client = TestClient(app)

class TestMilestone3AuthAndAI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_initial_accounts()

    # =========================================================================
    # 1. TWO SEPARATE ADMINISTRATOR ACCOUNTS & AUTHENTICATION
    # =========================================================================
    def test_01_admin1_login_and_access(self):
        """Test Admin 1 can log in, receive valid token, and access admin endpoints."""
        res = client.post("/api/auth/login", json={
            "email": "admin1@yieldsense.com",
            "password": "Admin1@2026!"
        })
        self.assertEqual(res.status_code, 200, f"Admin 1 login failed: {res.text}")
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "Administrator")
        token = data["access_token"]

        # Verify /api/auth/me
        res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["email"], "admin1@yieldsense.com")
        self.assertEqual(res_me.json()["role"], "Administrator")

        # Admin 1 can access /api/admin/stats
        res_stats = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_stats.status_code, 200)
        stats = res_stats.json()
        self.assertGreaterEqual(stats["total_administrators"], 2)

        # Admin 1 can access /api/admin/users
        res_users = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_users.status_code, 200)

        # Admin 1 can access PDF report
        res_pdf = client.get("/api/admin/farmers/report", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_pdf.status_code, 200)
        self.assertEqual(res_pdf.headers.get("content-type"), "application/pdf")
        self.assertTrue(res_pdf.content.startswith(b"%PDF"))

    def test_02_admin2_login_and_access(self):
        """Test Admin 2 is a separate database user and has full admin access."""
        res = client.post("/api/auth/login", json={
            "email": "admin2@yieldsense.com",
            "password": "Admin2@2026!"
        })
        self.assertEqual(res.status_code, 200, f"Admin 2 login failed: {res.text}")
        data = res.json()
        self.assertEqual(data["role"], "Administrator")
        token = data["access_token"]

        # Verify /api/auth/me for Admin 2
        res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["email"], "admin2@yieldsense.com")
        self.assertEqual(res_me.json()["role"], "Administrator")

        # Admin 2 can access /api/admin/stats
        res_stats = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_stats.status_code, 200)

    # =========================================================================
    # 2. FARMER AUTHENTICATION & ROLE-BASED ACCESS PROTECTION
    # =========================================================================
    def test_03_farmer_login_and_restrictions(self):
        """Test Farmer accounts cannot access Admin endpoints."""
        res = client.post("/api/auth/login", json={
            "email": "farmer1@yieldsense.com",
            "password": "Farmer1@2026!"
        })
        self.assertEqual(res.status_code, 200, f"Farmer 1 login failed: {res.text}")
        data = res.json()
        self.assertEqual(data["role"], "Farmer")
        farmer_token = data["access_token"]

        # Farmer accessing /api/auth/me
        res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {farmer_token}"})
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["role"], "Farmer")

        # Farmer must be FORBIDDEN from accessing Admin Stats (403)
        res_adm_stats = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {farmer_token}"})
        self.assertEqual(res_adm_stats.status_code, 403, "Farmer should not access admin stats")

        # Farmer must be FORBIDDEN from accessing Admin User Management (403)
        res_adm_users = client.get("/api/admin/users", headers={"Authorization": f"Bearer {farmer_token}"})
        self.assertEqual(res_adm_users.status_code, 403, "Farmer should not access admin users")

        # Farmer must be FORBIDDEN from downloading Admin Farmer Report (403)
        res_adm_rep = client.get("/api/admin/farmers/report", headers={"Authorization": f"Bearer {farmer_token}"})
        self.assertEqual(res_adm_rep.status_code, 403, "Farmer should not download admin farmer report")

    def test_04_auth_durability_and_token_validation(self):
        """Test token durability, invalid token handling, and unauthorized requests."""
        # Unauthenticated request to protected endpoint
        res_unauth = client.get("/api/auth/me")
        self.assertEqual(res_unauth.status_code, 401)

        # Invalid token
        res_invalid = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
        self.assertEqual(res_invalid.status_code, 401)

    # =========================================================================
    # 3. GENERAL-PURPOSE AI ASSISTANT (ALL TOPIC TYPES)
    # =========================================================================
    def test_05_ai_agriculture_question(self):
        """Test AI assistant answers agriculture questions with domain accuracy."""
        res = client.post("/api/chat", json={
            "message": "What is the best soil for rice?"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("reply", data)
        self.assertTrue(len(data["reply"]) > 50)
        self.assertTrue(any(w in data["reply"].lower() for w in ["clay", "alluvial", "loam", "water", "ph"]))

    def test_06_ai_programming_python_question(self):
        """Test AI assistant answers programming questions naturally (What is Python?)."""
        res = client.post("/api/chat", json={
            "message": "What is Python?"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(any(w in data["reply"].lower() for w in ["programming", "interpreted", "language", "syntax", "fastapi", "pandas"]))

    def test_07_ai_programming_java_factorial(self):
        """Test AI assistant provides code (Write a Java program for factorial)."""
        res = client.post("/api/chat", json={
            "message": "Write a Java program for factorial."
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(any(w in data["reply"].lower() for w in ["public class", "factorial", "recursive", "iterative", "java"]))

    def test_08_ai_tech_ram_vs_rom(self):
        """Test AI assistant explains computer hardware (RAM vs ROM)."""
        res = client.post("/api/chat", json={
            "message": "What is the difference between RAM and ROM?"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(any(w in data["reply"].lower() for w in ["volatile", "read-only", "bios", "memory"]))

    def test_09_ai_science_photosynthesis(self):
        """Test AI assistant explains natural science concepts (Photosynthesis)."""
        res = client.post("/api/chat", json={
            "message": "Explain photosynthesis."
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(any(w in data["reply"].lower() for w in ["chlorophyll", "sunlight", "carbon dioxide", "glucose", "light", "calvin"]))

    def test_10_ai_machine_learning_simply(self):
        """Test AI assistant explains ML concepts (Explain machine learning simply)."""
        res = client.post("/api/chat", json={
            "message": "Explain machine learning simply."
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(any(w in data["reply"].lower() for w in ["supervised", "algorithm", "data", "pattern", "predict"]))

    def test_11_ai_career_interview_prep(self):
        """Test AI assistant provides career and interview guidance."""
        res = client.post("/api/chat", json={
            "message": "Help me prepare for an interview."
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(any(w in data["reply"].lower() for w in ["star", "situation", "task", "action", "result", "questions"]))

    def test_12_ai_writing_caption_ideas(self):
        """Test AI assistant provides creative writing and caption ideas."""
        res = client.post("/api/chat", json={
            "message": "Give me ideas for an Instagram caption."
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(any(w in data["reply"].lower() for w in ["caption", "hashtag", "tech", "harvest", "nature"]))

    def test_13_ai_conversational_and_weather(self):
        """Test AI assistant handles conversational and weather inquiries gracefully."""
        res_hi = client.post("/api/chat", json={"message": "Hello, how are you?"})
        self.assertEqual(res_hi.status_code, 200)
        self.assertTrue(len(res_hi.json()["reply"]) > 20)

        res_weath = client.post("/api/chat", json={"message": "What is today's weather?"})
        self.assertEqual(res_weath.status_code, 200)
        self.assertTrue(any(w in res_weath.json()["reply"].lower() for w in ["weather", "temperature", "rainfall", "yieldsense"]))

    def test_14_ai_project_context_personalized_lookups(self):
        """Test AI assistant retrieves real user DB data for authenticated queries without hallucination."""
        # Login Farmer 1
        l_res = client.post("/api/auth/login", json={"email": "farmer1@yieldsense.com", "password": "Farmer1@2026!"})
        f_token = l_res.json()["access_token"]

        # Ask about registered farm
        res_farm = client.post(
            "/api/chat",
            json={"message": "Tell me about my farm."},
            headers={"Authorization": f"Bearer {f_token}"}
        )
        self.assertEqual(res_farm.status_code, 200)
        self.assertIn("Green Acres Farm", res_farm.json()["reply"])
        self.assertIn("25.5 acres", res_farm.json()["reply"])

        # Ask about latest prediction
        res_pred = client.post(
            "/api/chat",
            json={"message": "What is my latest prediction?"},
            headers={"Authorization": f"Bearer {f_token}"}
        )
        self.assertEqual(res_pred.status_code, 200)
        self.assertIn("Wheat", res_pred.json()["reply"])
        self.assertIn("4,350", res_pred.json()["reply"])

    def test_15_ai_chat_history_and_clear(self):
        """Test authenticated user chat history retrieval and clearing."""
        l_res = client.post("/api/auth/login", json={"email": "farmer2@yieldsense.com", "password": "Farmer2@2026!"})
        token = l_res.json()["access_token"]

        # Send a message
        client.post("/api/chat", json={"message": "What is Python?"}, headers={"Authorization": f"Bearer {token}"})

        # Retrieve history
        res_hist = client.get("/api/chat/history", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_hist.status_code, 200)
        self.assertGreaterEqual(len(res_hist.json()), 1)

        # Clear history
        res_clr = client.delete("/api/chat/history", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_clr.status_code, 200)

        # Verify empty
        res_after = client.get("/api/chat/history", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(len(res_after.json()), 0)

    # =========================================================================
    # 4. PRESERVATION OF EXISTING ML & CORE FEATURES
    # =========================================================================
    def test_16_preserved_ml_prediction_and_analytics(self):
        """Verify ML yield forecast and analytics endpoints remain 100% operational."""
        # Yield Prediction API
        pred_payload = {
            "State": "Punjab",
            "Crop": "Wheat",
            "Soil_Type": "Loamy",
            "Fertilizer": "DAP",
            "N": 85.0,
            "P": 45.0,
            "K": 50.0,
            "Rainfall_mm": 140.0,
            "Temperature_C": 26.5,
            "Soil_pH": 6.8,
            "Year": 2026
        }
        res_pred = client.post("/api/predict/yield", json=pred_payload)
        self.assertEqual(res_pred.status_code, 200)
        self.assertIn("predicted_yield_kg_per_acre", res_pred.json())

        # Model Info API
        res_info = client.get("/api/ml/model-info")
        self.assertEqual(res_info.status_code, 200)
        self.assertEqual(res_info.json()["best_model_name"], "LinearRegression")

        # System Analytics API
        res_adm_login = client.post("/api/auth/login", json={"email": "admin1@yieldsense.com", "password": "Admin1@2026!"})
        adm_token = res_adm_login.json()["access_token"]
        res_sys = client.get("/api/analytics/system", headers={"Authorization": f"Bearer {adm_token}"})
        self.assertEqual(res_sys.status_code, 200)

        # Insights Risk Analysis
        res_risk = client.post("/api/insights/analyze", json=pred_payload)
        self.assertEqual(res_risk.status_code, 200)
        self.assertIn("risk_score_percent", res_risk.json())
        self.assertIn("overall_risk_level", res_risk.json())

if __name__ == "__main__":
    unittest.main()
