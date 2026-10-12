# SpendSense AI — Smart Personal Finance & Expense Management

SpendSense AI is an intelligent full-stack personal finance application built to help users log income and expenses, visualize financial health, set category budgets with warning alerts, export reports, and receive grounded spending advice from an AI assistant.

---

## 1. System Architecture & Tech Stack

```mermaid
graph TD
    Client[React 19 + Vite Frontend\nRender Static Site / Nginx] -->|HTTPS REST API / Bearer JWT| Backend[FastAPI Backend\nRender Docker Web Service]
    Backend -->|SQLAlchemy 2.x ORM| Database[(PostgreSQL 16\nRender Managed DB)]
    Backend -->|Alembic Migrations| DBInit[Schema Migrations]
    Backend -->|Context-Grounded Facts| AI[AI Service\nGemini / Groq / OpenAI / Local Engine]
```

- **Frontend:** React 19, Vite, Recharts (analytics & graphs), Lucide icons, responsive CSS3.
- **Backend:** Python 3.11, FastAPI, Pydantic v2 (validation & settings), Uvicorn.
- **Persistence:** SQLAlchemy 2.x, Alembic migrations, PostgreSQL 16 (Render Managed DB / Docker) & SQLite (local zero-config fallback).
- **Security:** bcrypt password hashing (salted rounds), PyJWT authentication (`HS256`), strict multi-tenant data isolation, non-permissive CORS.
- **AI Integration:** Context-grounded AI service with pluggable provider architecture (Google Gemini 1.5 Flash, Groq Cloud, OpenAI GPT-4o-mini, deterministic local fallback engine).
- **Deployment Platform:** Render (Frontend: Static Site; Backend: Docker Web Service; DB: PostgreSQL 16) with GitHub Continuous Deployment.

---

## 2. Key Features

- **Full Transaction CRUD:** Log, view, edit, and delete transactions with instant totals and balance updates.
- **Precision Financial Math:** Server-side `Decimal` calculations avoiding floating-point rounding errors.
- **Multi-Tenant User Security:** User registration, login, and JWT session handling. User records and budgets are strictly isolated per account.
- **Interactive Analytics Dashboard:** Real-time net current balance, total income, total expenses, monthly trend bar charts, and category distribution pie charts.
- **Search & Multi-Filter Ledger:** Instant search by title, category filtering, type filtering (`income` vs `expense`), date-range filtering, and pagination.
- **Budget Alerts & Utilization:** Monthly category budget caps with visual progress bars and automatic warning indicators (⚡ Near Limit at 80%, ⚠️ Over Budget at 100%).
- **Financial Reports & CSV Export:** Download user transactions as RFC 4180 compliant CSV files with active filter parameters.
- **Grounded AI Spending Assistant:** Chat with an AI assistant that analyzes verified database facts (spent amounts, top categories, budget overruns) rather than hallucinating numbers.

---

## 3. Repository Directory Structure

```text
spendSenseai/
├── render.yaml               # Render Blueprint deployment specification
├── docker-compose.yml        # Docker Compose configuration (Postgres + Backend + Frontend)
├── .env.example              # Environment variables template with documentation
├── .gitignore                # Comprehensive Git ignore rules (secrets, venv, DB, build artifacts)
├── DEPLOYMENT_AUDIT.md       # Pre-deployment audit report & verification log
├── README.md                 # Complete documentation & deployment guide
└── SpendSense-AI/
    ├── backend/
    │   ├── alembic/          # Alembic database migration scripts
    │   │   └── versions/     # Initial schema DDL migration (77a877cdc72e)
    │   ├── alembic.ini       # Alembic migration configuration
    │   ├── app/
    │   │   ├── main.py       # FastAPI application root, CORS, health endpoint (/health)
    │   │   ├── core/         # Settings (Pydantic), security (JWT, bcrypt)
    │   │   ├── db/           # SQLAlchemy engine, connection pooling, session dependency
    │   │   ├── models/       # SQLAlchemy models (User, Expense, Budget)
    │   │   ├── schemas/      # Pydantic validation schemas
    │   │   ├── services/     # Business logic (CRUD, Budgets, Reports, AI)
    │   │   └── api/          # API v1 routes & dependencies
    │   ├── tests/            # Automated pytest test suite (100% pass rate)
    │   ├── Dockerfile        # Production Dockerfile (dynamic PORT, alembic migrations)
    │   ├── requirements.txt  # Python package dependencies
    │   └── .dockerignore     # Docker build context ignore rules
    └── frontend/
        └── frontend/         # React + Vite application
            ├── src/
            │   ├── components/# UI components (Dashboard, Budgets, Reports, Transactions, AI)
            │   ├── api.js    # Centralized API client (supports VITE_API_BASE_URL)
            │   ├── App.jsx   # Root view orchestrator
            │   └── App.css   # Clean, responsive styles
            ├── dist/         # Production build output (published on Render Static Site)
            ├── Dockerfile    # Nginx container build (optional/local)
            ├── nginx.conf    # Nginx SPA rewrite configuration
            ├── package.json  # NPM dependencies & scripts
            └── .dockerignore # Frontend Docker ignore rules
```

---

## 4. Local Development Setup (Windows PowerShell)

### Prerequisites
- Python 3.11+
- Node.js 20+ and npm
- (Optional) Docker Desktop

### A. Backend Setup
```powershell
# Navigate to backend directory
cd E:\spendSenseai\SpendSense-AI\backend

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### B. Frontend Setup
```powershell
# Navigate to frontend directory
cd E:\spendSenseai\SpendSense-AI\frontend\frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
- Frontend UI: `http://localhost:5173`

---

## 5. Docker Local Development (Windows)

To build and run the full stack (PostgreSQL 16 + FastAPI + React Nginx) locally:

1. **Start Docker Desktop** on Windows (from Start Menu).
2. **Build and launch containers:**
   ```powershell
   cd E:\spendSenseai
   docker compose up --build -d
   ```
3. **Inspect container status & logs:**
   ```powershell
   docker compose ps
   docker compose logs -f backend
   ```
4. **Test backend health inside container:**
   ```powershell
   curl http://localhost:8000/health
   ```
5. **Stop containers:**
   ```powershell
   docker compose down
   ```

---

## 6. Automated Testing & Verification

Run the automated test suite in the backend virtual environment:
```powershell
cd E:\spendSenseai\SpendSense-AI\backend
.\.venv\Scripts\pytest.exe -v
```

**Test Results:**
- `test_auth_and_isolation.py`: Registration, bcrypt hashing, JWT validation, multi-tenant isolation, anonymous query isolation, `/health` and `/` endpoints (**4/4 PASSED**).
- `test_budgets.py`: Category limits, real-time spent math, warning thresholds at 80%, exceeded thresholds at 100% (**1/1 PASSED**).
- `test_crud_expenses.py`: Create, Read, Update, Delete transactions, 404 handling, input validation (**3/3 PASSED**).
- `test_reports_and_ai.py`: Financial aggregation summaries, RFC 4180 CSV generation, AI fact grounding (**2/2 PASSED**).
- **Total: 10 passed in ~5.7s (100% pass rate).**

Verify frontend production compilation:
```powershell
cd E:\spendSenseai\SpendSense-AI\frontend\frontend
npm run build
```
*(Build compiles cleanly with zero errors).*

---

## 7. Render Production Deployment Guide

### Architecture Overview
- **Frontend:** Render Static Site (React 19 + Vite build). Free, global CDN, automated HTTPS, zero container overhead.
- **Backend:** Render Web Service (built from `SpendSense-AI/backend/Dockerfile`).
- **Database:** Render Managed PostgreSQL 16.
- **AI Assistant:** Google Gemini 1.5 Flash (or Groq Cloud / OpenAI) called securely from backend.

### Plan & Cost Considerations (Render)
- **Render Static Sites:** 100% Free tier available with continuous deployment on Git push.
- **Render Web Services:** Free tier spins down after 15 minutes of inactivity; spins up on incoming request in ~30–50s. (Starter plan: $7/month for zero spin-down).
- **Render Managed PostgreSQL:** Free tier is active for 30 days. For persistent production, upgrade to the Starter plan ($7/month) or connect an external Postgres provider like Neon / Supabase.

---

### Method A: Blueprint Deployment (render.yaml) — Recommended

1. Push your code to GitHub (see Section 8 below).
2. Log in to [Render Dashboard](https://dashboard.render.com/).
3. Click **Blueprints** → **New Blueprint Instance**.
4. Select your connected GitHub repository (`spendSenseai`).
5. Render detects `render.yaml` automatically and configures:
   - `spendsense-db` (PostgreSQL)
   - `spendsense-backend` (Docker Web Service)
   - `spendsense-frontend` (Static Site)
6. When prompted in the dashboard, enter your AI API key (e.g. `GEMINI_API_KEY`).
7. Click **Apply**.
8. Once deployed, copy your backend URL (`https://spendsense-backend-xxxx.onrender.com`) and paste it as `VITE_API_BASE_URL` in the frontend static site settings, then trigger a quick redeploy.

---

### Method B: Manual Dashboard Configuration

If configuring manually step-by-step:

#### Step 1: Create PostgreSQL Database
1. In Render Dashboard, click **New +** → **PostgreSQL**.
2. **Name:** `spendsense-db`
3. **Database:** `spendsensedb`
4. **User:** `spendsense_user`
5. **Region:** Oregon (US West) or Frankfurt (choose nearest to you).
6. **Plan:** Free (or Starter).
7. Click **Create Database**.
8. After creation, copy the **Internal Database URL** (e.g. `postgres://spendsense_user:password@dpg-xxxx:5432/spendsensedb`).

#### Step 2: Deploy Backend Web Service
1. In Render Dashboard, click **New +** → **Web Service**.
2. Connect your GitHub repository.
3. Select **Docker** environment.
4. **Root Directory:** `SpendSense-AI/backend`
5. **Dockerfile Path:** `./Dockerfile`
6. **Health Check Path:** `/health`
7. In **Environment Variables**, add:
   | Key | Value | Description |
   |-----|-------|-------------|
   | `DATABASE_URL` | *(Paste Internal Database URL from Step 1)* | Render internal PostgreSQL URI |
   | `SECRET_KEY` | *(Generate a random 32-byte string)* | JWT signing secret |
   | `ALGORITHM` | `HS256` | JWT algorithm |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 24-hour expiration |
   | `CORS_ORIGINS` | `*` (or your frontend Render URL) | Allowed origins |
   | `AI_PROVIDER` | `gemini` (or `groq` / `mock`) | Active AI engine |
   | `GEMINI_API_KEY` | *(Your Google AI Studio API key)* | LLM API key |
8. Click **Create Web Service**.
9. Wait for build and deployment. Verify logs show:
   `INFO: Application startup complete.` and health check passes.
10. Copy your live backend URL (e.g., `https://spendsense-backend.onrender.com`).

#### Step 3: Deploy Frontend Static Site
1. In Render Dashboard, click **New +** → **Static Site**.
2. Connect your GitHub repository.
3. **Root Directory:** `SpendSense-AI/frontend/frontend`
4. **Build Command:** `npm install && npm run build`
5. **Publish Directory:** `dist`
6. In **Environment Variables**, add:
   | Key | Value |
   |-----|-------|
   | `VITE_API_BASE_URL` | `https://spendsense-backend.onrender.com` (from Step 2) |
7. Under **Redirects / Rewrites**, add an SPA rewrite rule:
   - **Type:** `Rewrite`
   - **Source Path:** `/*`
   - **Destination Path:** `/index.html`
8. Click **Create Static Site**.
9. Once built, open the generated static site URL (e.g., `https://spendsense-frontend.onrender.com`).

---

## 8. GitHub Setup (Windows PowerShell)

Follow these exact commands to initialize and connect your repository:

> [!IMPORTANT]
> Real credentials or `.env` files must NEVER be committed to Git. The `.gitignore` has been verified to protect all secrets and database files.

```powershell
# 1. Open PowerShell and navigate to the project directory
cd E:\spendSenseai

# 2. Initialize Git
git init -b main

# 3. Check status to verify that .env, .venv, node_modules, and *.db are ignored
git status

# 4. Stage tracked project files
git add .

# 5. Commit changes
git commit -m "feat: complete SpendSense AI production deployment setup for Render"

# 6. Add your GitHub remote repository (replace with your real GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/spendSenseai.git

# 7. Push to GitHub main branch
git push -u origin main
```

---

## 9. Post-Deployment Verification & Testing Checklist

Once deployed on Render, execute these verification checks:

1. **Health Check:** Open `https://<backend-url>/health` in browser — should return `{"status": "ok", ...}`.
2. **API Documentation:** Open `https://<backend-url>/docs` — Swagger UI should render with all routes.
3. **User Registration & Login:** In the frontend, click **Sign In** → **Register** to create an account. Verify JWT token is received.
4. **CRUD Ledger:** Add a transaction (e.g. ₹500 for Food). Edit it. Delete an expense. Verify real-time balance calculations.
5. **Persistence Test:** Trigger a backend restart in Render Dashboard. Reload the frontend — verify all transactions remain intact.
6. **Budget Alerts:** Create a budget limit. Add transactions exceeding 80% and 100% to verify warning badges.
7. **CSV Export:** Click **Export CSV** in Reports tab and confirm download.
8. **AI Assistant:** Open the AI drawer and ask: *"How much did I spend this month?"*. Verify that the assistant answers with the exact logged numbers.
9. **Inspect Logs:** Go to **Logs** in Render Dashboard to monitor request streams and diagnose errors.
10. **Redeployment & Rollback:** Every `git push` to `main` triggers automated rebuild. To roll back an issue, navigate to **Deploys** in Render Dashboard and click **Rollback to this deploy**.
