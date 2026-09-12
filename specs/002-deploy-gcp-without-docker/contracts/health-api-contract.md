# Contract: Service Health Check API

**Feature**: [spec.md](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/specs/002-deploy-gcp-without-docker/spec.md) | **Date**: 2026-09-11

This contract defines the unauthenticated health probe endpoint consumed by Google Cloud load balancers, Cloud Run startup/liveness probes, and deployment validation scripts.

---

## Endpoint Specification

- **Path**: `GET /health`
- **Authentication**: None (Public)
- **Response Format**: `application/json`

---

## Response Schema

### 200 OK (System Healthy or Gracefully Degraded)

```json
{
  "status": "ok",
  "version": "0.1.0",
  "environment": "production",
  "database": {
    "status": "connected",
    "engine": "postgresql"
  },
  "cache": {
    "status": "available",
    "engine": "in-memory"
  },
  "dependencies": {
    "the_graph": "configured",
    "coingecko": "configured"
  }
}
```

### Response Field Descriptions

| Field | Type | Description |
| :--- | :--- | :--- |
| `status` | String | `"ok"` when core API and calculation engines are ready |
| `version` | String | Semantic version of backend service |
| `environment` | String | Operating mode: `"production"`, `"staging"`, or `"development"` |
| `database.status` | String | `"connected"` or `"fallback_sqlite"` |
| `database.engine` | String | Underlying database dialect (`"postgresql"` or `"sqlite"`) |
| `cache.status` | String | `"available"` or `"degraded"` |
| `dependencies.*` | String | Status of external provider configuration (`"configured"` or `"missing"`) |

---

## HTTP Status Codes

| Status Code | Description |
| :--- | :--- |
| `200 OK` | Service is running and capable of processing risk requests |
| `503 Service Unavailable` | Service is in an unrecoverable state or fatal startup error |
