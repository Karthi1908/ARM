# Quickstart: Google Cloud Deployment Without Docker

**Feature**: [spec.md](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/specs/002-deploy-gcp-without-docker/spec.md) | **Date**: 2026-09-11

This guide provides end-to-end verification steps for deploying the entire Crypto Risk Manager application to Google Cloud Platform using native source-based deployments (Cloud Run with Google Cloud Buildpacks) without Docker installed locally.

---

## 1. Prerequisites

1. **Google Cloud SDK (`gcloud`)**:
   Ensure `gcloud` CLI is installed on your workstation.
   ```powershell
   gcloud --version
   ```
2. **Authenticated GCP Account**:
   ```powershell
   gcloud auth login
   gcloud auth application-default login
   ```
3. **Target Project Set**:
   ```powershell
   gcloud config set project YOUR_PROJECT_ID
   ```
4. **Required GCP APIs Enabled**:
   ```powershell
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com
   ```
5. **No Docker Needed**: Confirm no local Docker daemon is required or running.

---

## 2. Environment Configuration

Prepare the production configuration file or environment variables. Copy the template:
```powershell
Copy-Item .env.example .env.gcp
```
Fill in the necessary values:
- `PRIVY_APP_ID`
- `PRIVY_APP_SECRET`
- `THE_GRAPH_API_KEY`
- `COINGECKO_API_KEY`
- `DATABASE_URL` (optional: defaults to SQLite fallback if PostgreSQL not configured)

---

## 3. Deployment Procedure

### Option A: Automated One-Command Script (Recommended)

Run the deployment automation script from the repository root:

```powershell
# Deploy both backend and frontend to us-central1
.\deploy-gcp.ps1 -Region us-central1
```

Or on Linux / macOS / Cloud Shell:
```bash
chmod +x deploy-gcp.sh
./deploy-gcp.sh --region us-central1
```

### Option B: Manual Source Deployment via `gcloud` CLI

If deploying step-by-step manually:

#### Step 1: Deploy Backend API
```powershell
cd backend
gcloud run deploy agentic-risk-backend `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars PRIVY_APP_ID="your_id",THE_GRAPH_API_KEY="your_key"
cd ..
```
*Note the returned public Service URL (e.g. `https://agentic-risk-backend-xyz.run.app`).*

#### Step 2: Verify Backend Health
```powershell
curl https://agentic-risk-backend-xyz.run.app/health
```
*Expected output*: `{"status":"ok", ...}`

#### Step 3: Deploy Frontend Web Application
```powershell
cd frontend
gcloud run deploy agentic-risk-frontend `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars NEXT_PUBLIC_API_URL="https://agentic-risk-backend-xyz.run.app"
cd ..
```
*Note the returned public Frontend URL (e.g. `https://agentic-risk-frontend-xyz.run.app`).*

---

## 4. End-to-End Validation Scenarios

### Scenario 1: Web Interface Verification
1. Open the frontend public URL in a web browser.
2. Confirm the dashboard loads in under 3 seconds without TLS warnings.
3. Observe live risk indicators and market metrics populated from the cloud backend.

### Scenario 2: Non-Custodial Authentication & Portfolio Discovery
1. Click **Connect Wallet** on the live frontend.
2. Authenticate using Privy social or wallet login.
3. Verify that the portfolio indexes balances through The Graph without requesting private keys.

### Scenario 3: Service Scaling & Recovery Test
1. Allow the Cloud Run backend service to idle down to 0 instances.
2. Send a new request via the frontend.
3. Verify the service starts up smoothly and delivers accurate portfolio responses.
