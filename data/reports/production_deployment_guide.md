# Production Deployment Guide: Gold & Tamil Nadu Real Estate Intelligence Platform

## Architecture Overview

```
                      [ PUBLIC USERS / MENTOR ]
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │     VERCEL HOSTING      │
                     │  (Next.js 14 Frontend)  │
                     │  <project>.vercel.app   │
                     └────────────┬────────────┘
                                  │ Next.js Rewrites Reverse Proxy
                                  │ (/api/*, /dashboard, /real-estate-dashboard)
                                  ▼
                     ┌─────────────────────────┐
                     │     RENDER HOSTING      │
                     │  (FastAPI Backend API)  │
                     │  <backend>.onrender.com │
                     └────────────┬────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       ┌─────────────────────┐        ┌───────────────────────┐
       │ gold_intelligence.db│        │    real_estate.db     │
       │    (7,460 rows)     │        │ (203 observations /   │
       │ (2000 - Nov 5, 2026)│        │   38 TN districts)    │
       └─────────────────────┘        └───────────────────────┘
```

---

## 1. Local Repository Status

- Git repository initialized on branch `main`.
- `.gitignore` configured to safely exclude `.venv/`, `node_modules/`, `.next/`, and environment secrets.
- Seed databases packaged in `data/`:
  - `data/gold_intelligence.db` (2.3 MB, 7,460 daily rows)
  - `data/real_estate.db` (360 KB, 203 verified observations across all 38 districts)
- Infrastructure-as-Code files in place:
  - `render.yaml` (Render Web Service definition)
  - `.python-version` (`3.11.9`)
  - `vercel.json` (Root Vercel orchestration)
  - `frontend/next.config.mjs` (Reverse proxy rewrites)

---

## 2. Step 1: Push Code to GitHub

Execute the following commands from the project root (`/Users/abijeeva/Documents/gold&realestate`):

```bash
# 1. Stage all files
git add .

# 2. Commit the codebase
git commit -m "feat: complete gold and real estate intelligence platform with vercel and render configs"

# 3. Create a new repository on GitHub (e.g. named 'gold-realestate-intelligence')
# 4. Link your remote and push
git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO-NAME>.git
git branch -M main
git push -u origin main
```

---

## 3. Step 2: Deploy Backend to Render

1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** $\rightarrow$ **Web Service**.
3. Connect your GitHub repository (`<YOUR-REPO-NAME>`).
4. Configure the Web Service settings:
   - **Name**: `gold-realestate-api` (or your preferred name)
   - **Region**: `Oregon (US West)` or `Frankfurt (EU)`
   - **Branch**: `main`
   - **Root Directory**: `.` (leave empty or set to root)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Under **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.9`
   - `APP_ENV`: `production`
   - `CORS_ORIGINS`: `*`
6. Under **Advanced Settings**:
   - **Health Check Path**: `/health`
7. Click **Create Web Service**.
8. Once deployed, note your Render URL:  
   `https://<service-name>.onrender.com`
9. Test the backend health check in your browser:  
   `https://<service-name>.onrender.com/health`  
   *(Expected response: `{"status": "healthy", "gold_database": "connected", "real_estate_database": "connected"}`)*

---

## 4. Step 3: Deploy Frontend to Vercel

1. Log in to [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** $\rightarrow$ **Project**.
3. Import your GitHub repository (`<YOUR-REPO-NAME>`).
4. Configure the Project settings:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click `Edit` and select `frontend` (or leave root since root `vercel.json` delegates to `frontend`).
   - **Build and Output Settings**: Defaults are automatically detected by Next.js.
5. Under **Environment Variables**, add:
   - **Name**: `NEXT_PUBLIC_API_BASE_URL`
   - **Value**: `https://<service-name>.onrender.com` (your Render backend URL from Step 2)
6. Click **Deploy**.
7. Once deployed, note your Vercel URL:  
   `https://<project-name>.vercel.app`

---

## 5. Mentor Demonstration URL Checklist

Your mentor can access all three dashboards and API endpoints from the single Vercel domain:

| Dashboard / Service | URL Path | What the Mentor Will See |
| :--- | :--- | :--- |
| **Next.js Main Platform** | `https://<project-name>.vercel.app/` | 4 simplified sections, live Tamil Nadu 1 Sovereign rate (₹1,07,080), interactive jewellery calculator, and common-man buying forecasts. |
| **Gold Editorial Terminal** | `https://<project-name>.vercel.app/dashboard` | Institutional full-screen terminal with Chart.js historical curves, multi-horizon forecasts, and macro stress tests. |
| **Tamil Nadu Real Estate Engine** | `https://<project-name>.vercel.app/real-estate-dashboard` | 38-district coverage map, guideline vs market price spreads, locality valuations, and rental yield tables. |
| **API Health & Diagnostic** | `https://<project-name>.vercel.app/health` | Live database row counts, system uptime, and memory status. |
| **Interactive API Swagger** | `https://<service-name>.onrender.com/docs` | OpenAPI documentation for all 30+ endpoints. |

---

## 6. Verification Checklist

- [x] All 134 automated unit and integration tests passing.
- [x] Next.js frontend updated with ₹1,07,080 sovereign base and interactive jewellery calculator.
- [x] Common-man forecast table displays 30d, 90d, 180d, and 365d predictions with wedding/accumulation advisory.
- [x] Both SQLite databases intact and versioned.
- [x] Reverse proxy rewrites in `next.config.mjs` eliminate CORS errors and unify access under one domain.
