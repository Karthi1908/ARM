# Implementation Plan: Deploy Entire Application to Google Cloud Without Docker

**Branch**: `002-deploy-gcp-without-docker` | **Date**: 2026-09-11 | **Spec**: [spec.md](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/specs/002-deploy-gcp-without-docker/spec.md)

**Input**: Feature specification from `/specs/002-deploy-gcp-without-docker/spec.md`

## Summary

Deploy the entire Crypto Risk Manager application (FastAPI quantitative risk engine and Next.js 14 web application) to Google Cloud Platform using native serverless source deployment on Google Cloud Run via Google Cloud Buildpacks. This completely eliminates the need for a local Docker installation, local container building, or custom Dockerfile maintenance on developer machines, while delivering autoscaling, automatic TLS certificates, secure secrets injection, and independent service lifecycles.

## Technical Context

**Language/Version**: Python 3.11+ (Backend API), TypeScript 5.4 / Node.js 20+ (Frontend Web App)

**Primary Dependencies**: 
- Backend: FastAPI, Uvicorn, Pydantic, NumPy, SciPy, Pandas, SQLAlchemy, aiosqlite, asyncpg
- Frontend: Next.js 14, React 18, @privy-io/react-auth, viem, lucide-react
- Cloud Deployment: Google Cloud SDK (`gcloud`), Google Cloud Run, Google Cloud Buildpacks

**Storage**: Google Cloud SQL (PostgreSQL) for production persistence with automatic local SQLite fallback for staging/ephemeral preview instances.

**Testing**: `pytest` for backend verification, `npm run build` for frontend compilation, and live HTTP health check probes (`/health`).

**Target Platform**: Google Cloud Platform (Google Cloud Run serverless container runtime built remotely from source).

**Project Type**: Full-stack web application (Backend API + Frontend SPA/SSR).

**Performance Goals**:
- Source packaging and cloud build completion in < 10 minutes.
- Frontend initial interactive load < 2.5 seconds on public domain.
- Backend API p95 response latency < 300ms.
- 99.9% uptime availability with zero cold-start failures.

**Constraints**:
- **Zero Local Docker Functionality**: No Docker daemon, CLI, or local image build steps permitted.
- **Zero Secrets Leakage**: No API keys, credentials, or secrets committed to source repositories.
- **Non-Custodial Architecture**: Cloud environments must never handle or store user private keys or wallet credentials.
- **Automated TLS**: All public endpoints must serve valid HTTPS certificates managed by GCP.

**Scale/Scope**: Configuration files (`Procfile`, `.gcloudignore`), deployment scripts (`deploy-gcp.ps1`, `deploy-gcp.sh`), environment templates, and health check validation.

## Constitution Check

*GATE: Pre-design and post-design verification against `.specify/memory/constitution.md`*

| Principle / Gate | Requirement | Status | Notes |
| :--- | :--- | :---: | :--- |
| **I. Non-Custodial by Default** | Never store, handle, or request private keys or wallet seeds. | **PASS** | Authentication remains strictly client-side via Privy / World ID. Cloud workloads handle only read-only indexing and mathematical computation. |
| **II. Read-First, Execute-Only-on-Consent** | No autonomous rebalance executions. | **PASS** | Cloud services expose advisory routes; transactions require interactive client-side wallet signatures. |
| **III. Deterministic Risk Math** | Deterministic calculations, versioned math. | **PASS** | Cloud deployment runs exact Python numerical libraries without alteration to risk math core. |
| **IV. Data Provenance & Graceful Degradation** | Record timestamps, graceful fallbacks. | **PASS** | Fallbacks for Redis, SQLite, and external oracles remain active and monitored via `/health`. |
| **V. Pluggable Adapters (EVM Scope)** | EVM execution connectors decoupled from core. | **PASS** | Unaffected by cloud hosting target. |
| **VI. Observability & Auditability** | Transparent logging and traceability. | **PASS** | Cloud Run streams stdout/stderr directly to Google Cloud Logging for auditable operation logs. |
| **VII. Progressive Disclosure UX** | Summary indicators with drill-down depth. | **PASS** | Frontend delivered via Cloud Run retains complete progressive disclosure interface hierarchy. |
| **Quality Gate: Zero Secrets Leakage** | Prevent API keys/credentials in repo. | **PASS** | Enforced via `.gcloudignore`, Secret Manager / runtime env flags, and `.env.gcp.example`. |

## Project Structure

### Documentation (this feature)

```text
specs/002-deploy-gcp-without-docker/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan output)
├── research.md          # Technical research & architectural decisions
├── data-model.md        # Entities, schemas, and state transitions
├── quickstart.md        # Step-by-step verification guide
├── contracts/           # Interface contracts
│   ├── deployment-cli-contract.md
│   └── health-api-contract.md
├── checklists/
│   └── requirements.md  # Quality validation checklist
└── tasks.md             # Phase 2 output (/speckit-tasks output - downstream)
```

### Source Code (repository root)

```text
.
├── backend/
│   ├── Procfile                # [NEW] Cloud Run Buildpack entrypoint definition
│   ├── .gcloudignore           # [NEW] Source packaging exclusion list for backend
│   ├── requirements.txt        # Python dependency manifest for Cloud Buildpacks
│   └── src/
│       └── api/
│           └── main.py         # FastAPI application with /health probe endpoint
├── frontend/
│   ├── .gcloudignore           # [NEW] Source packaging exclusion list for frontend
│   ├── package.json            # Node.js manifest with dynamic port binding in start script
│   └── src/                    # Next.js web application
├── .env.gcp.example            # [NEW] Environment variables template for GCP deployment
├── deploy-gcp.ps1              # [NEW] Automated PowerShell deployment script for Windows
├── deploy-gcp.sh               # [NEW] Automated Bash deployment script for Linux/macOS/Cloud Shell
└── render.yaml                 # Existing Render configuration (preserved)
```

**Structure Decision**: Multi-service web application layout. The existing `backend/` and `frontend/` directories are maintained and enhanced with non-intrusive Google Cloud deployment manifests (`Procfile`, `.gcloudignore`, scripts) that leave existing local workflows and Docker files unaffected.

## Complexity Tracking

*No constitutional violations identified. No complexity exemptions required.*
