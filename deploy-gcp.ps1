<#
.SYNOPSIS
    Deploys Crypto Risk Manager to Google Cloud Platform using native Cloud Run Buildpacks (Zero Docker Required).

.DESCRIPTION
    Automates the source packaging, remote Cloud Build, and Cloud Run provisioning for both
    FastAPI backend and Next.js frontend without requiring a local Docker daemon or installation.

.PARAMETER ProjectId
    The Google Cloud Project ID to deploy into. Defaults to current active gcloud project.

.PARAMETER Region
    The Google Cloud region for deployment. Default: us-central1.

.PARAMETER BackendOnly
    Deploy only the backend API service.

.PARAMETER FrontendOnly
    Deploy only the frontend web application.

.PARAMETER SkipHealthCheck
    Skip the automated post-deployment health check ping.

.PARAMETER EnvFile
    Path to environment configuration file. Default: .env.gcp (falls back to .env).

.PARAMETER CloudSqlInstance
    Optional Cloud SQL instance connection string (project:region:instance) for database binding.
#>

[CmdletBinding()]
param (
    [string]$ProjectId = "agentic-risk-hack",
    [string]$Region = "us-central1",
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$SkipHealthCheck,
    [string]$EnvFile = ".env.gcp",
    [string]$CloudSqlInstance = ""
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Crypto Risk Manager - Google Cloud Deployment (No Docker) " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# 1. Verify Prerequisites
# ---------------------------------------------------------------------------
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow

$gcloudCmd = Get-Command "gcloud" -ErrorAction SilentlyContinue
if (-not $gcloudCmd) {
    Write-Host "ERROR: Google Cloud SDK (gcloud) CLI is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Google Cloud CLI: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
    exit 1
}

# Verify active gcloud authentication
$activeAccount = (& gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null)
if (-not $activeAccount) {
    Write-Host "ERROR: No active Google Cloud account detected. Please run 'gcloud auth login' first." -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Authenticated as: $activeAccount" -ForegroundColor Green

# Resolve Project ID
if (-not $ProjectId) {
    $ProjectId = (& gcloud config get-value project 2>$null)
    if (-not $ProjectId -or $ProjectId -eq "(unset)") {
        $envProject = [System.Environment]::GetEnvironmentVariable("GCP_PROJECT_ID")
        if ($envProject) {
            $ProjectId = $envProject
        } else {
            Write-Host "ERROR: No Google Cloud Project specified. Provide -ProjectId 'your-project-id' or run 'gcloud config set project your-project-id'." -ForegroundColor Red
            exit 2
        }
    }
}
Write-Host "  [OK] Target Project: $ProjectId" -ForegroundColor Green
Write-Host "  [OK] Target Region:  $Region" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 2. Ensure Required Google Cloud APIs are Enabled
# ---------------------------------------------------------------------------
Write-Host "`n[2/6] Verifying Google Cloud APIs (Cloud Run and Cloud Build)..." -ForegroundColor Yellow
& gcloud services enable run.googleapis.com cloudbuild.googleapis.com --project $ProjectId
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to enable required Google Cloud APIs on project $ProjectId." -ForegroundColor Red
    exit 2
}
Write-Host "  [OK] Required APIs enabled." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 3. Parse Environment Configuration and Secrets
# ---------------------------------------------------------------------------
Write-Host "`n[3/6] Reading environment configuration..." -ForegroundColor Yellow
$resolvedEnvFile = $EnvFile
if (-not (Test-Path $resolvedEnvFile)) {
    if (Test-Path ".env") {
        $resolvedEnvFile = ".env"
    } else {
        $resolvedEnvFile = ""
    }
}

$envMap = @{}
if ($resolvedEnvFile) {
    Write-Host "  Loading variables from: $resolvedEnvFile" -ForegroundColor Cyan
    Get-Content $resolvedEnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line.Split("=", 2)
            $k = $parts[0].Trim()
            $v = $parts[1].Trim().Trim('"').Trim("'")
            $envMap[$k] = $v
        }
    }
}

# Collect backend environment parameters
$backendEnvList = @()
$keysToPass = @(
    "PRIVY_APP_ID",
    "PRIVY_APP_SECRET",
    "DATABASE_URL",
    "REDIS_URL",
    "THE_GRAPH_API_KEY",
    "COINGECKO_API_KEY",
    "ONEINCH_API_KEY",
    "GEMINI_API_KEY"
)

foreach ($key in $keysToPass) {
    $val = ""
    if ($envMap.ContainsKey($key) -and $envMap[$key]) {
        $val = $envMap[$key]
    } else {
        $envVal = [System.Environment]::GetEnvironmentVariable($key)
        if ($envVal) {
            $val = $envVal
        }
    }
    if ($val) {
        $backendEnvList += "$key=$val"
    }
}

$backendEnvArg = ""
if ($backendEnvList.Count -gt 0) {
    $backendEnvArg = ($backendEnvList -join ",")
}

$envBackendService = [System.Environment]::GetEnvironmentVariable("BACKEND_SERVICE_NAME")
if ($envBackendService) { $BackendServiceName = $envBackendService } else { $BackendServiceName = "agentic-risk-backend" }

$envFrontendService = [System.Environment]::GetEnvironmentVariable("FRONTEND_SERVICE_NAME")
if ($envFrontendService) { $FrontendServiceName = $envFrontendService } else { $FrontendServiceName = "agentic-risk-frontend" }

$BackendUrl = ""

# ---------------------------------------------------------------------------
# 4. Deploy Backend API Service (Cloud Run via Buildpacks)
# ---------------------------------------------------------------------------
if (-not $FrontendOnly) {
    Write-Host "`n[4/6] Deploying Backend API to Cloud Run from source (Zero Docker)..." -ForegroundColor Yellow
    Write-Host "  Service: $BackendServiceName" -ForegroundColor Cyan
    Write-Host "  Source:  ./backend" -ForegroundColor Cyan

    $deployArgs = @(
        "run", "deploy", $BackendServiceName,
        "--source", "./backend",
        "--region", $Region,
        "--project", $ProjectId,
        "--allow-unauthenticated",
        "--memory", "1Gi",
        "--cpu", "1",
        "--min-instances", "0",
        "--max-instances", "10",
        "--quiet"
    )

    if ($backendEnvArg) {
        $deployArgs += @("--set-env-vars", $backendEnvArg)
    }

    if ($CloudSqlInstance) {
        $deployArgs += @("--add-cloudsql-instances", $CloudSqlInstance)
    }

    & gcloud @deployArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Backend Cloud Run deployment failed." -ForegroundColor Red
        exit 3
    }

    $BackendUrl = (& gcloud run services describe $BackendServiceName --region $Region --project $ProjectId --format="value(status.url)" 2>$null)
    Write-Host "  [OK] Backend API deployed successfully!" -ForegroundColor Green
    Write-Host "  Endpoint: $BackendUrl" -ForegroundColor Cyan
} else {
    # Resolve existing backend URL for frontend binding
    $BackendUrl = (& gcloud run services describe $BackendServiceName --region $Region --project $ProjectId --format="value(status.url)" 2>$null)
}

# ---------------------------------------------------------------------------
# 5. Verify Backend Health Check
# ---------------------------------------------------------------------------
if (-not $FrontendOnly -and -not $SkipHealthCheck -and $BackendUrl) {
    Write-Host "`n[5/6] Verifying Backend Health Check..." -ForegroundColor Yellow
    $healthUrl = "$BackendUrl/health"
    try {
        $response = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 15
        Write-Host "  [OK] Health check passed!" -ForegroundColor Green
        Write-Host "  Status: $($response.status) | Database: $($response.database.engine) | Cache: $($response.cache.engine)" -ForegroundColor Cyan
    } catch {
        Write-Warning "Health check query to $healthUrl returned a warning: $_"
    }
} else {
    Write-Host "`n[5/6] Skipping health check verification." -ForegroundColor Gray
}

# ---------------------------------------------------------------------------
# 6. Deploy Frontend Web Application (Cloud Run via Buildpacks)
# ---------------------------------------------------------------------------
$FrontendUrl = ""
if (-not $BackendOnly) {
    Write-Host "`n[6/6] Deploying Frontend Web App to Cloud Run from source (Zero Docker)..." -ForegroundColor Yellow
    Write-Host "  Service: $FrontendServiceName" -ForegroundColor Cyan
    Write-Host "  Source:  ./frontend" -ForegroundColor Cyan

    $frontendEnv = "NEXT_PUBLIC_API_URL=$BackendUrl"
    if ($envMap.ContainsKey("PRIVY_APP_ID") -and $envMap["PRIVY_APP_ID"]) {
        $frontendEnv += ",NEXT_PUBLIC_PRIVY_APP_ID=$($envMap['PRIVY_APP_ID'])"
    }

    $frontendDeployArgs = @(
        "run", "deploy", $FrontendServiceName,
        "--source", "./frontend",
        "--region", $Region,
        "--project", $ProjectId,
        "--allow-unauthenticated",
        "--memory", "512Mi",
        "--cpu", "1",
        "--min-instances", "0",
        "--max-instances", "10",
        "--set-env-vars", $frontendEnv,
        "--quiet"
    )

    & gcloud @frontendDeployArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Frontend Cloud Run deployment failed." -ForegroundColor Red
        exit 4
    }

    $FrontendUrl = (& gcloud run services describe $FrontendServiceName --region $Region --project $ProjectId --format="value(status.url)" 2>$null)
    Write-Host "  [OK] Frontend Web Application deployed successfully!" -ForegroundColor Green
    Write-Host "  Endpoint: $FrontendUrl" -ForegroundColor Cyan
}

# ---------------------------------------------------------------------------
# Deployment Summary
# ---------------------------------------------------------------------------
Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE (Zero Docker Used) " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
if ($BackendUrl) {
    Write-Host "  Backend API:    $BackendUrl" -ForegroundColor Cyan
    Write-Host "  Health Probe:   $BackendUrl/health" -ForegroundColor Cyan
    Write-Host "  API Docs:       $BackendUrl/docs" -ForegroundColor Cyan
}
if ($FrontendUrl) {
    Write-Host "  Web Dashboard:  $FrontendUrl" -ForegroundColor Cyan
}
Write-Host "============================================================`n" -ForegroundColor Green
exit 0
