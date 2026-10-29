# SentinelAI - Autonomous AI Security Operations Center

SentinelAI is a production-style, AI-assisted Security Operations Center (SOC)
platform. It ingests security events, normalizes them into a standard schema,
extracts ML features, correlates related events into incidents, investigates
them with an agent workflow, scores risk deterministically, and recommends
safe, human-approved response actions.

> **Safety first:** the system is a defensive platform. All response actions
> run in `SIMULATION_MODE=true` by default, are allowlisted, audited, and
> high-risk actions always require human approval (RBAC-protected).

## Current status

All phases have working foundations, covered by 28 passing backend tests:

- [x] Phase 1 - Foundation: monorepo, FastAPI + JSON logging, SQLAlchemy models,
      Alembic migrations, Redis client with graceful degradation, JWT auth
      (access + rotating refresh tokens) + RBAC, React/TS/Tailwind frontend,
      Docker Compose stack
- [x] Phase 2 - Event pipeline: `POST /api/v1/events` ingestion + normalization,
      event list/filter/get API, synthetic event generator
- [x] Phase 3 - ML (partial): feature engineering (auth / network / process
      features over sliding windows), persisted as `FeatureRecord` with
      `feature_version` tracking
- [x] Phase 4 - Incident engine (partial): entity-based correlation with
      gap-based time clustering on event timestamps, brute-force pattern
      detection, incidents API
- [x] Phase 5 - Agents (partial): `SOCState` + Supervisor agent with
      deterministic planning, `POST /incidents/{id}/investigate`
- [x] Phase 6 - Human-in-the-loop: response actions with approval gate,
      RBAC-protected approve/reject (SOC_ANALYST/ADMIN), audit logging,
      `SIMULATION_MODE`
- [x] Phase 7 - Dashboard: SOC overview with severity breakdown, active
      incident list, live system status
- [x] Phase 8 - Evaluation: harness producing measured metrics (confusion
      matrix, precision/recall/F1, ingestion throughput)

Planned next:

- [ ] Phase 3 (remaining): Isolation Forest / XGBoost training + inference,
      `ml_predictions` wiring
- [ ] Phase 5 (remaining): Investigation / Threat-Intel / MITRE / Reasoning /
      Response agents with LangGraph orchestration
- [ ] OpenSearch indexing + full-text event search, WebSocket live updates

## Tech stack

| Layer      | Technology                                   |
| ---------- | -------------------------------------------- |
| Backend    | Python 3.12, FastAPI, SQLAlchemy 2, Alembic  |
| Database   | PostgreSQL 16, Redis 7, OpenSearch 2         |
| Frontend   | React 18, TypeScript, Tailwind CSS, Vite     |
| Auth       | JWT (access + refresh rotation), bcrypt      |
| ML (P3)    | scikit-learn (Isolation Forest), XGBoost     |
| Agents(P5) | LangGraph with LLM provider abstraction      |

## Architecture

```mermaid
flowchart TD

A[Security Events] --> B[Event Normalizer]
B --> C[Feature Engineering]
C --> D[ML Detection]
D --> E[Correlation Engine]
E --> F[Incident Manager]
F --> G[Supervisor Agent]
G --> H[Investigation Agent]
G --> I[Threat Intelligence Agent]
G --> J[MITRE Agent]
H --> K[Reasoning Agent]
I --> K
J --> K
K --> L[Risk Engine]
L --> M[Response Planner]
M --> N{Human Approval}
N -->|Approved| O[Controlled Response]
N -->|Rejected| P[Close / Continue Investigation]
O --> Q[Audit Log]
P --> Q
```

## Getting started - full startup guide

### Prerequisites

- **Option A (full stack):** Docker Desktop
- **Option B (local dev):** Python 3.12+, Node.js 18+

---

### Option A - Full stack with Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

What this starts:

| Container  | Purpose                                                    |
| ---------- | ---------------------------------------------------------- |
| postgres   | PostgreSQL 16 (user data, events, incidents)               |
| redis      | Redis 7 (caching, rate limiting)                           |
| opensearch | OpenSearch 2 (event search; security plugins off for dev)  |
| backend    | FastAPI - runs `alembic upgrade head`, seeds reference data (roles, admin user, MITRE subset, default risk/response settings), then serves on :8000 |
| frontend   | nginx serving the built React app on :5173                 |

Verify the stack is healthy:

```bash
curl http://localhost:8000/health   # -> {"status":"ok",...}          (liveness)
curl http://localhost:8000/ready    # -> {"status":"ready","database":"up","redis":"up"}
```

- Frontend: http://localhost:5173
- API docs (Swagger): http://localhost:8000/docs

Log in with the seeded admin: `admin@sentinel.local` / `ChangeMe123!`
(configurable via `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`).

To stop: `docker compose down` (add `-v` to also wipe the database volumes).

---

### Option B - Local development without Docker

#### 1. Backend (API + database)

**Windows (PowerShell):**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1                # or: .venv\Scripts\activate  (cmd)
pip install -r requirements.txt

$env:DATABASE_URL = "sqlite:///./sentinel.db"   # quick start; or point at Postgres
alembic upgrade head                      # create the full schema
python -m app.seed                        # roles, admin user, MITRE subset, settings
uvicorn app.main:app --reload             # API at http://localhost:8000
```

**Linux / macOS (bash):**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL=sqlite:///./sentinel.db     # or postgresql+psycopg://...
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

To use PostgreSQL instead of SQLite, start just the infra containers and point
`DATABASE_URL` at it:

```bash
docker compose up -d postgres redis
# then set DATABASE_URL=postgresql+psycopg://sentinel:sentinel_dev_password@localhost:5432/sentinel
```

#### 2. Frontend (dashboard)

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs at http://localhost:5173 and proxies `/api` and
`/health` to the backend at `http://localhost:8000` (configurable via
`VITE_API_PROXY`). No CORS setup needed in dev.

#### 3. Log in

Open http://localhost:5173 and sign in with the seeded admin:

- Email: `admin@sentinel.local`
- Password: `ChangeMe123!`

---

### Try the full pipeline end-to-end

Once the backend is running (Docker or local), exercise the whole flow:

```bash
# 1. Get an admin token (needed for response/approval endpoints - RBAC)
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sentinel.local","password":"ChangeMe123!"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 2. Ingest 5 failed-login events for the same user/IP (normalization runs here)
for i in 1 2 3 4 5; do
curl -s -X POST http://localhost:8000/api/v1/events -H "Content-Type: application/json" -d '{
  "timestamp": "2026-09-14T10:00:00Z",
  "source": "auth-server",
  "event_type": "authentication_failure",
  "source_ip": "10.0.0.66",
  "destination_ip": "192.168.1.20",
  "destination_port": 22,
  "protocol": "SSH",
  "username": "svc_admin",
  "hostname": "server-01",
  "severity": "HIGH",
  "raw_message": "Failed password for svc_admin"
}' > /dev/null
done

# 3. Correlate events into incidents
curl -s -X POST "http://localhost:8000/api/v1/incidents/correlate?window_minutes=30&min_events=3"

# 4. Investigate the incident with the Supervisor agent (use an incident id from step 3)
# curl -s -X POST http://localhost:8000/api/v1/incidents/<INCIDENT_ID>/investigate

# 5. Propose a response action (requires Bearer token; HIGH risk -> PENDING_APPROVAL)
# curl -s -X POST http://localhost:8000/api/v1/responses \
#   -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"incident_id":"<INCIDENT_ID>","action_type":"block_test_ip","params":{"ip":"10.0.0.66"},"risk_class":"HIGH"}'

# 6. Approve it (simulated - no real system is touched)
# curl -s -X POST http://localhost:8000/api/v1/responses/<ACTION_ID>/approve \
#   -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"decision":"APPROVED","reason":"confirmed brute force"}'
```

### Demo data generator

Populate the SOC with synthetic events for local testing:

```bash
cd backend
python ../scripts/generate_events.py --count 50   # 50 random events across event types
```

### Run the evaluation harness

Produces measured (not fabricated) detection metrics and an ingestion
throughput benchmark; saves a report to `scripts/evaluation_report.json`:

```bash
cd backend
python ../scripts/evaluate.py
```

## Running tests

```bash
cd backend
pytest
```

28 tests cover: authentication + JWT refresh rotation, RBAC, database schema
integrity, Redis degradation behavior, event ingestion/normalization, feature
extraction, incident correlation, the Supervisor agent, and the RBAC-protected
approval workflow.

## API overview

| Method | Path                                   | Auth                 | Purpose                                   |
| ------ | -------------------------------------- | -------------------- | ----------------------------------------- |
| GET    | `/health`                              | none                 | Liveness                                  |
| GET    | `/ready`                               | none                 | DB + Redis readiness probe                |
| POST   | `/api/v1/auth/login`                   | none                 | Get access + refresh tokens               |
| POST   | `/api/v1/auth/refresh`                 | none (refresh token) | Rotate token pair                         |
| GET    | `/api/v1/auth/me`                      | Bearer               | Current user                              |
| GET    | `/api/v1/users`                        | Bearer               | List users                                |
| POST   | `/api/v1/users`                        | Bearer               | Create user                               |
| POST   | `/api/v1/events`                       | none (see notes)     | Ingest + normalize a security event       |
| GET    | `/api/v1/events`                       | none (see notes)     | List events (filter by type/IP/user)      |
| GET    | `/api/v1/events/{id}`                  | none (see notes)     | Get one event                             |
| POST   | `/api/v1/events/{id}/features`         | none (see notes)     | Extract + store ML features for an event  |
| POST   | `/api/v1/incidents/correlate`          | none (see notes)     | Run correlation over unlinked events      |
| GET    | `/api/v1/incidents`                    | none (see notes)     | List incidents                            |
| GET    | `/api/v1/incidents/{id}`               | none (see notes)     | Incident detail                           |
| POST   | `/api/v1/incidents/{id}/investigate`   | none (see notes)     | Run Supervisor agent on an incident       |
| POST   | `/api/v1/responses`                    | Bearer, SOC_ANALYST+ | Propose a response action                 |
| POST   | `/api/v1/responses/{id}/approve`       | Bearer, SOC_ANALYST+ | Approve/reject a response action          |

> **Note:** mutation endpoints under `/events` and `/incidents` are currently
> unauthenticated - planned for the Phase 8 hardening pass (see
> [Known limitations](#known-limitations)).

## Environment configuration

Copy `.env.example` to `.env`. Never commit real secrets. Key variables:

| Variable                  | Purpose                                            |
| ------------------------- | -------------------------------------------------- |
| `DATABASE_URL`            | SQLAlchemy connection string (SQLite for dev, Postgres for full stack) |
| `REDIS_URL`               | Redis connection URL                               |
| `OPENSEARCH_HOST`         | OpenSearch endpoint                                |
| `JWT_SECRET`              | Signing key (32+ bytes, change in production)      |
| `SIMULATION_MODE`         | `true` = all response actions are simulated        |
| `SEED_ADMIN_EMAIL`        | Seeded admin login                                 |
| `SEED_ADMIN_PASSWORD`     | Seeded admin password                              |
| `LLM_PROVIDER`            | `mock` (offline) by default; real providers in P5  |
| `VITE_API_PROXY`          | Vite dev proxy target (default `http://localhost:8000`) |

## Evaluation results (measured)

From `scripts/evaluate.py` on the synthetic labeled dataset (attack groups are
idealized and isolated; expect lower scores on noisy real-world data):

```text
sample_size: 180   incidents_created: 20
confusion_matrix:  tp=100  fp=0  tn=80  fn=0
precision: 1.0     recall: 1.0    f1: 1.0    accuracy: 1.0
correlation time:  0.04s
ingestion:         ~10,000 events/sec (PRD target: >= 100/sec)
```

## Security design principles

1. Security > autonomy - least privilege for every agent; no admin powers by default.
2. Evidence > LLM opinion - ML detection + deterministic rules + LLM reasoning.
3. High-risk actions require human approval; everything is audit-logged.
4. Log content is always untrusted data, never instructions.
5. No hardcoded credentials; no fabricated metrics.

## Known limitations

- `POST /events`, `POST /incidents/correlate` and `GET` read endpoints are not
  yet behind authentication - Phase 8 hardening will add RBAC.
- ML models (Isolation Forest, XGBoost) are not yet trained; the feature
  pipeline and evaluation harness are in place for them.
- Only the Supervisor agent exists; Investigation / Threat-Intel / MITRE /
  Reasoning / Response agents arrive with LangGraph orchestration (P5).
- OpenSearch is deployed but not yet used for event indexing/search.
- The dashboard is read-only (no incident detail page or WebSocket updates yet).

## Roadmap

| Phase | Scope                                          | Status              |
| ----- | ---------------------------------------------- | ------------------- |
| 1     | Foundation: repo, API, DB, Redis, auth, Docker | Done                |
| 2     | Event pipeline: ingestion, normalization       | Done                |
| 3     | ML: features, Isolation Forest, XGBoost        | Features done; models pending |
| 4     | Incident engine: correlation, risk             | Correlation done; risk engine pending |
| 5     | Agentic AI: LangGraph multi-agent workflow     | Supervisor done; agents pending |
| 6     | Human-in-the-loop approvals + simulation       | Done                |
| 7     | SOC dashboards & observability                 | Overview done; detail pages pending |
| 8     | Security hardening                             | Pending (partial: RBAC on approvals) |
| 9     | Evaluation & benchmarks                        | Harness done; ML benchmark pending |

## License

MIT - see [LICENSE](LICENSE).
