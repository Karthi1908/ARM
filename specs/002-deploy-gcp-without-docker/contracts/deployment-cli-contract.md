# Contract: Google Cloud Deployment CLI Interface

**Feature**: [spec.md](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/specs/002-deploy-gcp-without-docker/spec.md) | **Date**: 2026-09-11

This contract defines the command-line interface, input arguments, environment overrides, and exit codes for the automated Google Cloud deployment tooling (`deploy-gcp.ps1` / `deploy-gcp.sh`).

---

## Command Syntax

### PowerShell (Windows)
```powershell
.\deploy-gcp.ps1 [-ProjectId <string>] [-Region <string>] [-BackendOnly] [-FrontendOnly] [-SkipHealthCheck]
```

### Bash (macOS / Linux / Cloud Shell)
```bash
./deploy-gcp.sh [--project-id <string>] [--region <string>] [--backend-only] [--frontend-only] [--skip-health-check]
```

---

## Parameters & Options

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `-ProjectId`, `--project-id` | String | No | Active `gcloud config get-value project` | Target Google Cloud Project ID |
| `-Region`, `--region` | String | No | `us-central1` | Deployment compute region |
| `-BackendOnly`, `--backend-only` | Switch | No | `false` | Only build and deploy the backend API |
| `-FrontendOnly`, `--frontend-only`| Switch | No | `false` | Only build and deploy the frontend web application |
| `-SkipHealthCheck` | Switch | No | `false` | Skip post-deployment endpoint ping |

---

## Environment Overrides

The script automatically detects values from a local `.env` or from shell environment variables:

| Environment Variable | Description |
| :--- | :--- |
| `GCP_PROJECT_ID` | Fallback project ID if not passed via parameter |
| `GCP_REGION` | Fallback region if not passed via parameter |
| `BACKEND_SERVICE_NAME` | Name for backend Cloud Run service (default: `agentic-risk-backend`) |
| `FRONTEND_SERVICE_NAME` | Name for frontend Cloud Run service (default: `agentic-risk-frontend`) |

---

## Exit Codes

| Exit Code | Meaning |
| :--- | :--- |
| `0` | Successful deployment and health verification |
| `1` | Prerequisite missing (e.g., `gcloud` CLI not installed or unauthenticated) |
| `2` | Configuration error (e.g., invalid Project ID or missing mandatory secrets) |
| `3` | Backend build or deployment failure on Cloud Run |
| `4` | Frontend build or deployment failure on Cloud Run |
| `5` | Post-deployment health check failure |
