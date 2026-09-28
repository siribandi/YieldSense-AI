import io
import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.config import SessionLocal
from backend.app.db.models import User, Farm, Crop, Prediction

client = TestClient(app)

def run_verification():
    print("=" * 70)
    print("YIELDSENSE AI - FARMER RECORDS & PDF REPORT VERIFICATION")
    print("=" * 70)

    # 1. Register & Login as Administrator
    admin_email = "admin.verify.final@yieldsense.ai"
    admin_pass = "AdminPass123!"
    reg_res = client.post("/api/auth/register", json={
        "name": "System SuperAdmin",
        "email": admin_email,
        "password": admin_pass,
        "role": "Administrator"
    })
    
    login_res = client.post("/api/auth/login", json={
        "email": admin_email,
        "password": admin_pass
    })
    assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
    admin_token = login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[OK] Step 1: Admin successfully authenticated with JWT token.")

    # 2. Register & Login as normal Farmer to test RBAC
    farmer_email = "farmer.verify.final@yieldsense.ai"
    farmer_pass = "FarmerPass123!"
    client.post("/api/auth/register", json={
        "name": "Kishan Kumar",
        "email": farmer_email,
        "password": farmer_pass,
        "role": "Farmer"
    })
    f_login = client.post("/api/auth/login", json={
        "email": farmer_email,
        "password": farmer_pass
    })
    farmer_token = f_login.json()["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    print("[OK] Step 2: Normal Farmer registered & logged in.")

    # Seed farm & prediction for Farmer
    client.post("/api/farms", headers=farmer_headers, json={
        "farm_name": "Godavari Green Acres",
        "location": "Andhra Pradesh",
        "area": 12.5,
        "soil_type": "Alluvial"
    })
    client.post("/api/predictions", headers=farmer_headers, json={
        "State": "Andhra Pradesh",
        "Crop": "Rice",
        "Soil_Type": "Alluvial",
        "Fertilizer": "Urea",
        "N": 90, "P": 45, "K": 40,
        "Rainfall_mm": 1150.0,
        "Soil_pH": 6.8
    })

    # 3. Test Security (RBAC): Farmer MUST receive HTTP 403 Forbidden
    f_rep = client.get("/api/admin/farmers/report", headers=farmer_headers)
    assert f_rep.status_code == 403, f"Expected 403 Forbidden for farmer, got {f_rep.status_code}"
    print("[OK] Step 3: Security verified - Normal Farmer receives HTTP 403 Forbidden on Report endpoint.")

    # 4. Test Administrator calling Report endpoint: GET /api/admin/farmers/report
    rep_res = client.get("/api/admin/farmers/report", headers=admin_headers)
    assert rep_res.status_code == 200, f"Expected 200 OK for admin, got {rep_res.status_code}: {rep_res.text}"
    assert rep_res.headers.get("content-type") == "application/pdf", f"Expected PDF content-type, got {rep_res.headers.get('content-type')}"
    assert "attachment; filename=\"YieldSense_AI_Farmer_Report.pdf\"" in rep_res.headers.get("content-disposition", "")
    
    pdf_bytes = rep_res.content
    assert len(pdf_bytes) > 1000, f"PDF content too small: {len(pdf_bytes)} bytes"
    assert pdf_bytes.startswith(b"%PDF-"), "Invalid PDF signature! File does not start with %PDF-"
    print(f"[OK] Step 4: Admin downloaded valid PDF report ({len(pdf_bytes):,} bytes).")

    # 5. Save PDF to verify filesystem write
    output_pdf_path = PROJECT_ROOT / "YieldSense_AI_Farmer_Report.pdf"
    with open(output_pdf_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"[OK] Step 5: PDF saved to: {output_pdf_path} (Size: {len(pdf_bytes):,} bytes)")

    # 6. Verify Admin Users API returns real DB data
    users_res = client.get("/api/admin/users", headers=admin_headers)
    assert users_res.status_code == 200
    user_list = users_res.json()
    assert len(user_list) >= 2, f"Expected at least 2 users, got {len(user_list)}"
    print(f"[OK] Step 6: User records list verified ({len(user_list)} real database users returned).")

    # 7. Verify frontend file contains exact requested elements
    admin_users_jsx = PROJECT_ROOT / "frontend" / "src" / "pages" / "AdminUsers.jsx"
    with open(admin_users_jsx, "r", encoding="utf-8") as f:
        jsx_content = f.read()

    assert "Download Report" in jsx_content, "Download Report button text not found in AdminUsers.jsx"
    assert "Generating report..." in jsx_content, "'Generating report...' status string not found in AdminUsers.jsx"
    assert "Report downloaded successfully." in jsx_content, "'Report downloaded successfully.' string not found in AdminUsers.jsx"
    assert "Unable to generate report." in jsx_content, "'Unable to generate report.' string not found in AdminUsers.jsx"
    assert "YieldSense_AI_Farmer_Report.pdf" in jsx_content, "Target filename YieldSense_AI_Farmer_Report.pdf not found in AdminUsers.jsx"
    print("[OK] Step 7: Frontend AdminUsers.jsx verified with all exact button and state requirements.")

    print("=" * 70)
    print("ALL 7 VERIFICATION CRITERIA PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
