# Research: Google Cloud Deployment Without Docker

**Feature**: [spec.md](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/specs/002-deploy-gcp-without-docker/spec.md) | **Date**: 2026-09-11

## Overview

This document resolves the technical decisions and architectural strategies for deploying the full-stack Crypto Risk Manager (FastAPI backend + Next.js frontend) to Google Cloud Platform without requiring Docker on the developer workstation or running container daemon commands.

---

## Technical Investigations & Decisions

### 1. Cloud Compute Target: Cloud Run via Google Cloud Buildpacks vs. App Engine

- **Decision**: Use **Google Cloud Run with Source Deployment (`gcloud run deploy --source .`)** leveraging Google Cloud Buildpacks.
- **Rationale**:
  - **Zero Local Docker Prerequisite**: Developers and operators run `gcloud run deploy <service-name> --source .`. Google Cloud uploads the source directory to Cloud Build in Google Cloud, where Google Cloud Buildpacks detects the language and builds the deployment image remotely. No Docker daemon, Docker CLI, or Docker Desktop license is needed on the client machine.
  - **Serverless Autoscaling**: Cloud Run automatically scales from 0 to N instances, minimizing costs when idle and handling concurrency efficiently.
  - **Built-in HTTPS & Custom Domains**: Cloud Run provisions and manages TLS certificates automatically for all service endpoints.
  - **Independent Frontend & Backend Lifecycles**: Frontend and backend can be deployed, scaled, and configured independently without monolithic coupling.
- **Alternatives Considered**:
  - *Google App Engine (Standard Environment)*: Requires `app.yaml`. While App Engine also builds from source without Docker, App Engine Standard has stricter runtime constraints, slower rollout times, and more rigid networking compared to Cloud Run.
  - *Google Compute Engine (VM)*: Requires provisioning a persistent VM instance, installing Node/Python runtimes manually via SSH or startup scripts, and configuring Nginx reverse proxy. Rejected due to high operational maintenance overhead and lack of serverless auto-scaling.
  - *Firebase App Hosting / Hosting*: Good for static frontends, but Next.js 14 App Router with server-side components and API rewrites deploys more reliably and uniformly alongside the backend via Cloud Run.

---

### 2. Backend Service Runtime & Entrypoint Configuration

- **Decision**: Provide a `Procfile` and tailored `.gcloudignore` in `backend/` for the Python FastAPI application.
- **Specification**:
  - **Procfile**:
    ```procfile
    web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT --workers 2
    ```
  - **Runtime Detection**: Google Cloud Buildpacks automatically detects Python 3.11+ via `backend/requirements.txt`.
  - **Dynamic Port Binding**: Uvicorn binds to `$PORT` (passed by Cloud Run, default 8080).
  - **Source Exclusion (`.gcloudignore`)**: Excludes `.venv/`, `__pycache__/`, `.pytest_cache/`, `tests/`, `*.db`, and `.git/` to keep source bundle uploads lightweight (< 5MB) and secure.
- **Rationale**: Standardizes the execution model and guarantees zero reliance on Dockerfile syntax.

---

### 3. Frontend Next.js Service Runtime & Entrypoint Configuration

- **Decision**: Configure `frontend/package.json` start script to dynamically bind to Cloud Run's `$PORT`, along with a dedicated `frontend/.gcloudignore`.
- **Specification**:
  - **Script**:
    ```json
    "start": "next start -p ${PORT:-3000}"
    ```
  - **Build Command**: Buildpacks runs `npm run build` during remote cloud build.
  - **API Routing**: `NEXT_PUBLIC_API_URL` environment variable is provided to configure API request targets in production.
  - **Source Exclusion (`.gcloudignore`)**: Excludes `node_modules/`, `.next/`, `.env.local`, and build caches.
- **Rationale**: Next.js natively compiles into a standalone production server that binds to Cloud Run's `$PORT`.

---

### 4. Database Persistence Strategy

- **Decision**: Two-tiered persistence architecture:
  1. **Production**: Google Cloud SQL for PostgreSQL via Cloud Run Cloud SQL connector (`--add-cloudsql-instances` or connection string in `DATABASE_URL`).
  2. **Preview / Dev Staging**: Built-in fallback to SQLite with automated initialization if `DATABASE_URL` points to an SQLite path or PostgreSQL is temporarily unreachable.
- **Rationale**: Aligns with existing application code (`backend/src/config.py` supports both PostgreSQL asyncpg and SQLite fallback), enabling immediate testing without forcing instant Cloud SQL provisioning while ensuring production grade persistence.

---

### 5. Secrets and Configuration Management

- **Decision**: Manage application configuration and secrets using Google Cloud Secret Manager or direct Cloud Run environment variable injection (`--set-env-vars` / `--set-secrets`).
- **Required Variables**:
  - `PRIVY_APP_ID` (Public/Secret authentication identity)
  - `PRIVY_APP_SECRET` (Backend token verification)
  - `THE_GRAPH_API_KEY` (Portfolio balance indexing)
  - `COINGECKO_API_KEY` (Market price feeds)
  - `DATABASE_URL` (Database connection string)
- **Rationale**: Ensures strict zero-secrets leakage in compliance with Principle IV and Quality Gate 3 of the project constitution.

---

### 6. Deployment Automation Tooling

- **Decision**: Provide automated PowerShell (`deploy-gcp.ps1`) and POSIX Bash (`deploy-gcp.sh`) deployment scripts that run the full validation and deployment pipeline via `gcloud run deploy --source`.
- **Phases Executed by Script**:
  1. Verify `gcloud` CLI presence and active authentication.
  2. Prompt for or read target GCP Project ID and Region (default: `us-central1`).
  3. Deploy Backend API to Cloud Run (`agentic-risk-backend`).
  4. Extract Backend Public URL and run health check verification (`/health`).
  5. Deploy Frontend Web App to Cloud Run (`agentic-risk-frontend`) with `NEXT_PUBLIC_API_URL` set to the backend URL.
  6. Output live access endpoints and verification status.
- **Rationale**: Delivers a seamless one-command deployment experience without requiring users to write or understand complex container tooling.
