# Local Startup Guide 🚀

This document outlines the startup commands for running the **Backend** and **Frontend** independently.

---

## 1. Backend Service (FastAPI)

- **Port**: `8000`
- **Root Directory**: Project root (`agentic_risk_manager`)
- **API URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Docs (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Quick Run Scripts
- **Command Prompt / Double-Click**: [`start_backend.bat`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/start_backend.bat)
- **PowerShell**: [`start_backend.ps1`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/start_backend.ps1)

### Manual Terminal Commands

#### Windows (PowerShell)
```powershell
# From the project root
.\.venv\Scripts\python.exe -m uvicorn backend.src.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Windows (CMD)
```cmd
:: From the project root
.venv\Scripts\activate.bat
uvicorn backend.src.main:app --host 127.0.0.1 --port 8000 --reload
```

#### macOS / Linux (Bash)
```bash
# From the project root
source .venv/bin/activate
uvicorn backend.src.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 2. Frontend Service (Next.js 14)

- **Port**: `3000`
- **Root Directory**: `frontend/`
- **Dashboard URL**: [http://localhost:3000](http://localhost:3000)

### Quick Run Scripts
- **Command Prompt / Double-Click**: [`start_frontend.bat`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/start_frontend.bat)
- **PowerShell**: [`start_frontend.ps1`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/start_frontend.ps1)

### Manual Terminal Commands

#### Windows / macOS / Linux
```bash
# Navigate to the frontend folder
cd frontend

# Start Next.js development server
npm run dev
```

---

## 3. Environment & Configuration

| Service | Environment File | Notes |
| :--- | :--- | :--- |
| **Backend** | [`.env`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/.env) | Configures Privy credentials, DB URL (falls back to local SQLite `risk_manager.db` if PostgreSQL is offline), Redis URL (falls back to in-memory caching), and API keys. |
| **Frontend** | [`frontend/.env.local`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/frontend/.env.local) | Configures `NEXT_PUBLIC_PRIVY_APP_ID` and `NEXT_PUBLIC_API_URL` (`http://localhost:8000`). |
