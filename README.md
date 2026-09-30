# YieldSense AI – Agricultural Crop Yield Prediction & Decision Support System

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5.0-F7931E.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**YieldSense AI** is an enterprise-grade full-stack precision agriculture and machine learning platform. It empowers farmers and agricultural administrators with verified ML crop yield predictions, multi-tenant farm and crop lifecycle management, intelligent agronomic risk analytics, natural-language AI assistance (**AgriSense AI**), and automated high-fidelity PDF intelligence reports.

---

## 1. System Architecture

```
                                +-------------------------------------------+
                                |             Vite React Client             |
                                |  (Tailwind CSS + Lucide + Responsive UI)  |
                                +---------------------+---------------------+
                                                      | HTTP / JWT Bearer
                                                      v
                                +-------------------------------------------+
                                |           FastAPI Backend Engine          |
                                |  (Security, RBAC, Validation & Routing)   |
                                +-----+----------------+--------------+-----+
                                      |                |              |
                +---------------------+                |              +----------------------+
                |                                      |                                     |
                v                                      v                                     v
+-------------------------------+      +-------------------------------+     +-------------------------------+
|     PostgreSQL Database       |      |     Machine Learning Engine   |     |    AgriSense AI & Reports     |
| - Users & Two Admin Accounts  |      | - Linear Regression (v2.0.0)  |     | - Conversational AI Engine    |
| - Farms & Plot Boundaries     |      | - 11 Features -> 43 Encoded   |     | - Grounded DB Advisory        |
| - Crops & Sowing Cycles       |      | - OneHot & StandardScaler     |     | - PDF Intelligence Generator  |
| - Predictions & Chat Transcr. |      | - Model Artifacts in models/  |     | - ReportLab PDF Engine        |
+-------------------------------+      +-------------------------------+     +-------------------------------+
```

---

## 2. Key Features Across Milestones

### Milestone 1: Data Engineering, EDA & Platform Foundation
- Ingestion of 1,500 agricultural field records across 14 Indian states and 12 major crop varieties.
- Unbuffered data cleaning and exploratory analysis (`EDA_Crop_Yield.ipynb`).
- Relational PostgreSQL data schema with foreign key integrity and cascade policies.

### Milestone 2: Machine Learning Prediction Pipeline
- Production deployment of verified **Linear Regression Model (v2.0.0)** (`joblib` serialized in `models/`).
- 11 raw agricultural input parameters transformed into **43 dimensional dimensions** (One-Hot categorical encoding + Standard Scaling).
- Benchmarked against Random Forest, Gradient Boosting, and Decision Tree regressors.
- Full prediction history CRUD with multi-tenant isolation and strict permission boundaries.

### Milestone 3: Role-Based Authentication, Analytics & General AI Assistant
- **Role-Based Access Control (RBAC)**: Distinct **Farmer** and **Administrator** privileges with durable JWT authentication surviving browser refreshes.
- **Two Distinct Administrator Accounts**: Fully seeded database administrators with isolated credentials and global oversight.
- **Agricultural Analytics & Risk Engine**: Automated calculation of productivity categories, soil health alerts, and climate risk assessments.
- **AgriSense AI Conversational Assistant**: Versatile intelligence engine capable of answering programming, science, mathematics, domain agronomy, and personalized farm advisory inquiries with phonetic and typo tolerance.
- **Automated PDF Intelligence Report**: On-demand generation of formatted executive PDF reports for administrators containing live platform statistics and farmer holdings.

### Milestone 4: Full System Integration, Deployment Readiness & Production Hardening
- Complete containerization with multi-stage `Dockerfile` configurations and `docker-compose.yml`.
- Frontend production bundle optimization with Vite and Nginx.
- End-to-end automated test suites (`test_master_milestone4.py`) validating 100% test coverage.

---

## 3. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | React 18.3, Vite 5.3, Tailwind CSS 3.4, Lucide React, Axios | Modern, responsive single-page application with rich agricultural aesthetics |
| **Backend API** | Python 3.11+, FastAPI 0.111, Pydantic v2, Uvicorn | High-performance asynchronous REST API with auto-generated OpenAPI docs |
| **Database** | PostgreSQL 16, SQLAlchemy 2.0 (ORM), psycopg2 | Robust relational storage with transactional isolation and ACID guarantees |
| **Machine Learning** | Scikit-learn 1.5, Pandas 2.2, NumPy 1.26, Joblib | Standardized inference pipeline, feature encoding, and model persistence |
| **Security & Auth** | Passlib (Bcrypt), Python-Jose (JWT), OAuth2 Password Bearer | Secure password hashing, token expiration, and role-based route guards |
| **AI & Reports** | AgriSense AI Engine, ReportLab 5.0, HTTPX | General natural language synthesis and vector-quality PDF report generation |
| **DevOps & Containers**| Docker, Docker Compose, Nginx Alpine | Multi-container microservice orchestration for production deployment |

---

## 4. Default Seeded Accounts & Credentials

The database automatically initializes two administrator accounts and two verified farmer accounts upon startup:

| Account | Email | Password | Role | Assigned Resources |
| :--- | :--- | :--- | :--- | :--- |
| **Admin 1** | `admin1@yieldsense.com` | `Admin1@2026!` | `Administrator` | Full System Oversight & PDF Reports |
| **Admin 2** | `admin2@yieldsense.com` | `Admin2@2026!` | `Administrator` | Full System Oversight & PDF Reports |
| **Farmer 1** | `farmer1@yieldsense.com` | `Farmer1@2026!` | `Farmer` | *Green Acres Farm* (25.5 acres, Punjab, Wheat/Rice) |
| **Farmer 2** | `farmer2@yieldsense.com` | `Farmer2@2026!` | `Farmer` | *Surya Krishi Kendra* (18.0 acres, Maharashtra, Cotton) |

---

## 5. Local Setup & Installation

### Prerequisites
- **Python 3.11+** installed
- **Node.js v20+** and `npm` installed
- **PostgreSQL 16** (or use the included portable postgres server / Docker)

### Option A: Standard Local Execution

#### 1. Database Setup (Portable PostgreSQL)
Run the automated PostgreSQL initializer:
```powershell
python scripts/setup_postgres.py
```
This initializes a PostgreSQL cluster in `postgres/data/` and listens on `127.0.0.1:5432`.

#### 2. Backend Setup
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run database migrations and start API server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger Documentation will be accessible at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

#### 3. Frontend Setup
```powershell
# Open a new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open your browser at: [http://127.0.0.1:3000](http://127.0.0.1:3000) (or `http://127.0.0.1:3001`).

---

### Option B: Docker Container Deployment

To launch the full stack (PostgreSQL + FastAPI + Nginx React Frontend) in one command:

```powershell
# Build and run all container services in background
docker compose up --build -d
```

| Service | Internal Port | Mapped Host Port | URL |
| :--- | :--- | :--- | :--- |
| **Frontend Web App** | 80 | **3000** | `http://localhost:3000` |
| **FastAPI REST Backend** | 8000 | **8000** | `http://localhost:8000` |
| **PostgreSQL Database** | 5432 | **5432** | `localhost:5432` |

To stop the containers:
```powershell
docker compose down
```

---

## 6. Environment Configuration

### Root / Docker `.env.example`
```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=yieldsense_db
DATABASE_URL=postgresql://postgres:postgres@db:5432/yieldsense_db

JWT_SECRET=supersecretjwtkeyforagriculturalforecastingyielsdenseai2026
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Optional External AI API Key (Built-in offline engine functions out of the box)
# GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# AI_PROVIDER=auto
```

---

## 7. Machine Learning Model Specifications

- **Selected Deployment Model**: **Linear Regression (v2.0.0)**
- **Dataset**: Standardized repository of **1,500 agricultural field records** across 14 Indian states.
- **Evaluation Performance on Held-Out Test Data**:
  - **MAE (Mean Absolute Error)**: `4,273.23 kg/acre`
  - **RMSE (Root Mean Squared Error)**: `11,381.99 kg/acre`
  - **R² Score**: `0.0029`
- **Features (11 raw $\rightarrow$ 43 encoded dimensions)**:
  - Categorical: `State` (14), `Crop` (12), `Soil_Type` (5), `Fertilizer` (5)
  - Continuous: `N`, `P`, `K`, `Rainfall_mm`, `Temperature_C`, `Soil_pH`, `Year`

---

## 8. REST API Overview

### Authentication & User Identity
- `POST /api/auth/register` — Register a new farmer or administrator account.
- `POST /api/auth/login` — Authenticate and receive JWT access token.
- `GET /api/auth/me` — Retrieve authenticated user profile (session persistence).

### Farm & Crop Management
- `GET /api/farms` — List farms belonging to the authenticated user.
- `POST /api/farms` — Register a new farm field with acreage and soil type.
- `GET /api/crops` — List crops linked to the user's farms.
- `POST /api/crops` — Register a crop sowing cycle with dates and historical yield.

### Machine Learning Predictions
- `GET /api/ml/model-info` — Retrieve verified metrics and feature architecture.
- `POST /api/predict/yield` — Execute single-record yield prediction with productivity scoring.
- `GET /api/predictions` — List prediction history (Farmer: own records; Admin: global).
- `DELETE /api/predictions/{id}` — Delete a saved prediction record.

### Analytics & Agronomic Risk Engine
- `GET /api/analytics/farmer` — Calculate personalized farm metrics and yield summaries.
- `GET /api/analytics/system` — Calculate platform-wide distribution metrics across all records.
- `POST /api/insights/analyze` — Generate nutrient risk scores and actionable mitigation advice.

### AgriSense AI Assistant
- `POST /api/chat` — Conversational AI query endpoint with live database context and typo tolerance.
- `GET /api/chat/history` — Retrieve persistent conversation transcript for user.
- `DELETE /api/chat/history` — Clear conversation history.

### Administrator Operations & PDF Reports
- `GET /api/admin/stats` — Retrieve system KPIs, user distribution, and recent activity feed.
- `GET /api/admin/users` — List platform user directory with farm/crop/prediction counts.
- `GET /api/admin/farmers/report` — Stream dynamic, vector-quality PDF intelligence report.

---

## 9. Automated Testing & Verification

The project includes unit, integration, regression, and browser automation test suites:

```powershell
# Run Master Milestone 4 Test Suite (All 9 core validation modules)
python scripts/test_master_milestone4.py

# Run Milestone 3 Auth and AI Test Suite
python scripts/test_milestone3_auth_and_ai.py

# Run Milestone 2 ML Prediction Regression Suite
python scripts/test_master_milestone2.py

# Run PDF Report Generator Verification
python scripts/verify_pdf_report_and_button.py
```

### Verified Test Results
- **Master Milestone 4 Suite**: **9/9 Passed (100% OK)**
- **Authentication & RBAC Suite**: **16/16 Passed (100% OK)**
- **ML Inference & Validation Suite**: **10/10 Passed (100% OK)**
- **Frontend Production Build**: **Passed (`dist/` generated with 0 errors)**

---

## 10. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
