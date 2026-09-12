#!/usr/bin/env bash
# ==============================================================================
# Crypto Risk Manager - Google Cloud Deployment Automation (Zero Docker Required)
# ==============================================================================
set -e

PROJECT_ID=""
REGION="us-central1"
BACKEND_ONLY=false
FRONTEND_ONLY=false
SKIP_HEALTH_CHECK=false
ENV_FILE=".env.gcp"
CLOUD_SQL_INSTANCE=""

print_usage() {
    echo "Usage: ./deploy-gcp.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --project-id <id>          Google Cloud Project ID (default: active gcloud project)"
    echo "  --region <region>          Deployment compute region (default: us-central1)"
    echo "  --backend-only             Deploy only backend API"
    echo "  --frontend-only            Deploy only frontend web application"
    echo "  --skip-health-check        Skip post-deployment health verification"
    echo "  --env-file <path>          Environment variables file (default: .env.gcp or .env)"
    echo "  --cloud-sql <instance>     Optional Cloud SQL instance connection string"
    echo "  --help                     Display this help message"
}

# Parse command-line flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --skip-health-check)
            SKIP_HEALTH_CHECK=true
            shift
            ;;
        --env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        --cloud-sql)
            CLOUD_SQL_INSTANCE="$2"
            shift 2
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1"
            print_usage
            exit 2
            ;;
    esac
done

echo "============================================================"
echo "  Crypto Risk Manager - Google Cloud Deployment (No Docker) "
echo "============================================================"

# 1. Verify Prerequisites
echo "[1/6] Checking prerequisites..."
if ! command -v gcloud &>/dev/null; then
    echo "ERROR: Google Cloud SDK (gcloud) CLI is not installed or not in PATH."
    echo "Install gcloud: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || true)
if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo "ERROR: No active Google Cloud account detected. Please run 'gcloud auth login' first."
    exit 1
fi
echo "  ✓ Authenticated as: $ACTIVE_ACCOUNT"

if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null || true)
    if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
        if [ -n "$GCP_PROJECT_ID" ]; then
            PROJECT_ID="$GCP_PROJECT_ID"
        else
            echo "ERROR: No Google Cloud Project specified. Provide --project-id <id> or run 'gcloud config set project <id>'."
            exit 2
        fi
    fi
fi
echo "  ✓ Target Project: $PROJECT_ID"
echo "  ✓ Target Region:  $REGION"

# 2. Enable Required APIs
echo ""
echo "[2/6] Verifying Google Cloud APIs (Cloud Run & Cloud Build)..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --project "$PROJECT_ID"
echo "  ✓ Required APIs enabled."

# 3. Read Environment Configuration
echo ""
echo "[3/6] Reading environment configuration..."
RESOLVED_ENV_FILE="$ENV_FILE"
if [ ! -f "$RESOLVED_ENV_FILE" ]; then
    if [ -f ".env" ]; then
        RESOLVED_ENV_FILE=".env"
    else
        RESOLVED_ENV_FILE=""
    fi
fi

ENV_VARS_LIST=()
if [ -n "$RESOLVED_ENV_FILE" ] && [ -f "$RESOLVED_ENV_FILE" ]; then
    echo "  Loading variables from: $RESOLVED_ENV_FILE"
    while IFS='=' read -r key val || [ -n "$key" ]; do
        # Ignore comments and empty lines
        [[ "$key" =~ ^#.*$ ]] && continue
        [ -z "$key" ] && continue
        
        # Strip quotes and trim
        key=$(echo "$key" | xargs)
        val=$(echo "$val" | xargs | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
        
        case "$key" in
            PRIVY_APP_ID|PRIVY_APP_SECRET|DATABASE_URL|REDIS_URL|THE_GRAPH_API_KEY|COINGECKO_API_KEY|ONEINCH_API_KEY|GEMINI_API_KEY)
                if [ -n "$val" ]; then
                    ENV_VARS_LIST+=("$key=$val")
                fi
                ;;
        esac
    done < "$RESOLVED_ENV_FILE"
fi

BACKEND_ENV_ARG=""
if [ ${#ENV_VARS_LIST[@]} -gt 0 ]; then
    BACKEND_ENV_ARG=$(IFS=,; echo "${ENV_VARS_LIST[*]}")
fi

BACKEND_SERVICE_NAME="${BACKEND_SERVICE_NAME:-agentic-risk-backend}"
FRONTEND_SERVICE_NAME="${FRONTEND_SERVICE_NAME:-agentic-risk-frontend}"
BACKEND_URL=""

# 4. Deploy Backend
if [ "$FRONTEND_ONLY" = false ]; then
    echo ""
    echo "[4/6] Deploying Backend API to Cloud Run from source (Zero Docker)..."
    echo "  Service: $BACKEND_SERVICE_NAME"
    echo "  Source:  ./backend"

    DEPLOY_CMD=(
        gcloud run deploy "$BACKEND_SERVICE_NAME"
        --source "./backend"
        --region "$REGION"
        --project "$PROJECT_ID"
        --allow-unauthenticated
        --memory "1Gi"
        --cpu "1"
        --min-instances "0"
        --max-instances "10"
        --quiet
    )

    if [ -n "$BACKEND_ENV_ARG" ]; then
        DEPLOY_CMD+=(--set-env-vars "$BACKEND_ENV_ARG")
    fi

    if [ -n "$CLOUD_SQL_INSTANCE" ]; then
        DEPLOY_CMD+=(--add-cloudsql-instances "$CLOUD_SQL_INSTANCE")
    fi

    "${DEPLOY_CMD[@]}"

    BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format="value(status.url)" 2>/dev/null)
    echo "  ✓ Backend API deployed successfully!"
    echo "  Endpoint: $BACKEND_URL"
else
    BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format="value(status.url)" 2>/dev/null || true)
fi

# 5. Verify Health Check
if [ "$FRONTEND_ONLY" = false ] && [ "$SKIP_HEALTH_CHECK" = false ] && [ -n "$BACKEND_URL" ]; then
    echo ""
    echo "[5/6] Verifying Backend Health Check..."
    HEALTH_URL="$BACKEND_URL/health"
    if curl -s -f -m 15 "$HEALTH_URL" > /dev/null; then
        echo "  ✓ Health check passed!"
    else
        echo "  WARNING: Health probe at $HEALTH_URL returned non-200 or timed out."
    fi
else
    echo ""
    echo "[5/6] Skipping health check verification."
fi

# 6. Deploy Frontend
FRONTEND_URL=""
if [ "$BACKEND_ONLY" = false ]; then
    echo ""
    echo "[6/6] Deploying Frontend Web App to Cloud Run from source (Zero Docker)..."
    echo "  Service: $FRONTEND_SERVICE_NAME"
    echo "  Source:  ./frontend"

    FRONTEND_ENV="NEXT_PUBLIC_API_URL=$BACKEND_URL"

    gcloud run deploy "$FRONTEND_SERVICE_NAME" \
        --source "./frontend" \
        --region "$REGION" \
        --project "$PROJECT_ID" \
        --allow-unauthenticated \
        --memory "512Mi" \
        --cpu "1" \
        --min-instances "0" \
        --max-instances "10" \
        --set-env-vars "$FRONTEND_ENV" \
        --quiet

    FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format="value(status.url)" 2>/dev/null)
    echo "  ✓ Frontend Web Application deployed successfully!"
    echo "  Endpoint: $FRONTEND_URL"
fi

echo ""
echo "============================================================"
echo "  🎉 DEPLOYMENT COMPLETE (Zero Docker Used) "
echo "============================================================"
if [ -n "$BACKEND_URL" ]; then
    echo "  Backend API:    $BACKEND_URL"
    echo "  Health Probe:   $BACKEND_URL/health"
    echo "  API Docs:       $BACKEND_URL/docs"
fi
if [ -n "$FRONTEND_URL" ]; then
    echo "  Web Dashboard:  $FRONTEND_URL"
fi
echo "============================================================"
echo ""
exit 0
