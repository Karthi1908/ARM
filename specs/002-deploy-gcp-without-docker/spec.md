# Feature Specification: Deploy Entire Application to Google Cloud Without Docker

**Feature Branch**: `002-deploy-gcp-without-docker`

**Created**: 2026-09-11

**Status**: Ready for Planning

**Input**: User description: "this entire application needs to be deployed to google cloud without any docker functionalities"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One-Action Source-to-Cloud Deployment (Priority: P1)

An operations engineer or developer needs to deploy the complete application (frontend user dashboard and backend analytics services) directly from the project source tree to Google Cloud without installing Docker locally, running a local container daemon, or writing container orchestration commands.

**Why this priority**: Eliminating local container prerequisites is the primary business requirement, enabling fast deployments from constrained workstations, local environments lacking Docker engine licenses or daemon privileges, and standardized cloud-native source workflows.

**Independent Test**: Can be tested by running the source-based deployment procedure on a clean workstation without Docker installed, verifying that both the web interface and API service are deployed to live cloud URLs and function together.

**Acceptance Scenarios**:

1. **Given** a developer workstation with the application codebase, cloud credentials, and no Docker engine installed or active, **When** the cloud deployment procedure is executed for the backend service, **Then** Google Cloud accepts the source code, builds and provisions the service remotely, and returns an active public HTTPS endpoint serving valid health check responses.
2. **Given** the deployed backend service endpoint, **When** the cloud deployment procedure is executed for the frontend web application, **Then** Google Cloud builds and serves the web application, automatically configured to route API interactions to the live backend service.
3. **Given** both frontend and backend are deployed, **When** an end user accesses the public web URL, **Then** the risk management interface loads completely, establishes secure connectivity to the cloud backend, and allows browsing portfolio metrics without transport errors.

---

### User Story 2 - Secure Environment Configuration & Secrets Provisioning (Priority: P2)

An administrator needs to configure sensitive production credentials (authentication app identifiers, blockchain indexer keys, market pricing keys, and database connection strings) securely in Google Cloud without hardcoding them into source files or committing them to version control.

**Why this priority**: Compliance with the project constitution mandates zero secrets leakage and strict isolation of sensitive API credentials across cloud environments.

**Independent Test**: Can be tested by injecting sample credentials into Google Cloud configuration and verifying that the live application correctly accesses external services while no secrets appear in plaintext source files or public build logs.

**Acceptance Scenarios**:

1. **Given** production API keys and database credentials, **When** cloud configuration is provisioned, **Then** all secrets are stored securely in cloud-managed configuration or secret storage and injected as environment variables at runtime.
2. **Given** an updated configuration parameter, **When** the deployment is refreshed, **Then** the running services adopt the updated configuration without requiring code modifications or downtime.
3. **Given** a service attempting to start with missing mandatory credentials, **When** runtime initialization occurs, **Then** the service logs a clear missing-configuration diagnostic and fails safely rather than running in an insecure state.

---

### User Story 3 - Persistent Application State & Data Continuity (Priority: P3)

A portfolio manager inputs trades, monitors risk metrics, and saves portfolio states. When services restart, scale, or receive updates, previously stored portfolios and configuration data must remain intact and accessible.

**Why this priority**: Business continuity requires that user portfolios, trade blotters, and historical risk assessments survive routine cloud instance recycling and new application version rollouts.

**Independent Test**: Can be tested by creating test portfolio deals in the deployed application, triggering a cloud service redeployment or restart, and verifying that all previously entered positions and risk calculations remain intact upon service recovery.

**Acceptance Scenarios**:

1. **Given** saved trades and portfolio positions in the deployed application, **When** a new version of the application is deployed to Google Cloud, **Then** existing data remains completely intact and accessible immediately after the update.
2. **Given** the backend service scaling from zero to active instances, **When** a user requests portfolio data, **Then** the newly started instance accesses the persistent data store and delivers the accurate portfolio state.

---

### User Story 4 - Continuous Operational Observability & Health Verification (Priority: P4)

A platform operator needs to monitor runtime availability, view operational logs, inspect error rates, and confirm service health through standardized health checks.

**Why this priority**: Cloud deployments must provide actionable observability to satisfy governance and auditability principles, enabling rapid diagnosis of network latency, third-party oracle timeouts, or service interruptions.

**Independent Test**: Can be tested by polling the public health endpoints of the deployed services and viewing real-time structured logs in the cloud platform console.

**Acceptance Scenarios**:

1. **Given** running services on Google Cloud, **When** an automated health probe queries the designated health check endpoint, **Then** the service returns an HTTP 200 status with component availability details in under 1 second.
2. **Given** an unexpected exception or external API timeout occurs during runtime, **When** the event happens, **Then** a structured error log entry is immediately recorded in the cloud logging stream with timestamp, severity level, and request correlation context.

---

### Edge Cases

- **Cold Start Latency**: How does the system behave when serverless instances scale down to zero and receive sudden traffic spikes? (Acceptance: Return responses within tolerable thresholds without timing out; display non-blocking loading states on the client).
- **External Dependency Outages**: How does the deployed application behave if external price or indexer services become temporarily unreachable? (Acceptance: The cloud service must gracefully degrade, returning cached or baseline data with clear staleness indicators as mandated by the constitution).
- **Cross-Origin Resource Sharing (CORS)**: How are requests handled between the frontend domain and backend API domain? (Acceptance: Cloud services must allow authorized HTTPS origins and reject unauthorized cross-origin requests).
- **Source Build Size Limits**: What happens if dependencies or build artifacts exceed cloud source upload limits? (Acceptance: Ignore unnecessary cache, test, and virtual environment directories via upload exclusion filters to maintain small deployment footprints).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST deploy the backend computational risk service to Google Cloud without requiring local Docker engine installation, local Docker commands, or custom container registry push steps.
- **FR-002**: The system MUST deploy the frontend web application to Google Cloud without requiring local Docker engine installation, local Docker commands, or custom container build scripts.
- **FR-003**: The deployment procedure MUST accept application source files directly and rely exclusively on Google Cloud native runtimes or cloud buildpack services to compile and execute workloads.
- **FR-004**: The deployment workflow MUST provide configuration exclusion rules to prevent temporary files, local databases, virtual environments, and local build artifacts from uploading to the cloud.
- **FR-005**: The cloud deployment configuration MUST support injection of all required environment variables and secrets (authentication parameters, external API keys, database connection strings) through secure cloud configuration mechanisms.
- **FR-006**: The system MUST expose public HTTPS endpoints with valid TLS certificates managed automatically by Google Cloud for both web and API services.
- **FR-007**: The backend service MUST provide an unauthenticated health check endpoint that reports operational status and dependency readiness for automated cloud monitoring and load balancing.
- **FR-008**: The cloud configuration MUST route cross-service communications between the frontend web application and backend API securely using configured base URLs without hardcoded hostnames.
- **FR-009**: The deployment MUST maintain persistent storage for portfolio data across instance restarts, autoscaling events, and rolling service deployments.
- **FR-010**: The cloud deployment MUST stream structured runtime stdout/stderr application logs to Google Cloud's centralized logging facility.
- **FR-011**: The deployment scripts and configuration manifests MUST execute successfully from standard developer command-line interfaces (PowerShell, Bash) and automated CI/CD pipelines.
- **FR-012**: The cloud architecture MUST adhere to non-custodial operational principles: no private keys or wallet credentials shall be accepted, processed, or retained in cloud service environments.

### Key Entities

- **Cloud Deployment Configuration**: Declarative service specification defining runtime version, entrypoint command, instance resource limits (CPU/Memory), scaling boundaries, and environment bindings.
- **Application Workload Service**: The executing cloud compute unit (frontend web interface or backend API engine) running on managed Google Cloud infrastructure.
- **Environment Secret / Parameter**: Key-value pairs representing external integration keys, authentication identifiers, and connectivity credentials managed securely outside source code.
- **Health Verification Record**: Operational payload capturing service availability, database connectivity, external provider status, and response latency.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Complete deployment of both frontend and backend workloads succeeds from a clean development environment with zero Docker tools or daemon installed.
- **SC-002**: End-to-end deployment time from initiation to live accessible public endpoints completes in under 10 minutes.
- **SC-003**: Web application loads interactively in user browsers in under 3 seconds under normal network conditions.
- **SC-004**: System maintains 99.9% uptime availability during operational monitoring periods.
- **SC-005**: 100% of sensitive API keys and production credentials are supplied via cloud configuration without appearing in source code repository commits.
- **SC-006**: Deployed services automatically recover from instance terminations or rolling updates with zero data loss for persisted user portfolios.

## Assumptions

- Deployments will be targeted to a Google Cloud project where the deploying operator has appropriate administrative or editor permissions.
- Google Cloud CLI (`gcloud`) or Google Cloud console/Cloud Shell is accessible to the operator for executing deployment commands.
- The backend API service will utilize Google Cloud's native source-based compute platform (such as Cloud Run via Google Cloud Buildpacks or App Engine), building the container image automatically in the cloud without requiring Docker on the developer's computer.
- The frontend Next.js application will be deployed using either Google Cloud's managed serverless runtime (Cloud Run source deploy / App Engine) or Firebase Hosting / Cloud Storage static hosting with API proxying.
- Database persistence will leverage a managed Google Cloud relational database (such as Cloud SQL) for production continuity, while supporting an automated local file fallback for temporary preview environments.
- All communications are conducted over standard secure HTTPS/TLS protocols.
