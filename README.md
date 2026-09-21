# Apex Compliance Engine — Enterprise B2B SaaS Platform

Apex Compliance Engine is an institutional-grade, multi-tenant compliance ops platform built for financial institutions, Fintech platforms, and regulatory compliance teams. It enables organizations to automate batch transaction ingestion, perform deterministic sanctions and anti-money laundering (AML) screening, triage flagged compliance violations, and generate regulator-ready PDF audit reports.

---

## 2. Features

- **Multi-Tenant Architecture**: Strict organization-level data isolation across tenants using tenant-scoped database queries.
- **Role-Based Access Control (RBAC)**: Enforces granular role permissions across `Admin`, `Compliance Officer`, and `Auditor` roles.
- **Automated CSV Ingestion Pipeline**: High-throughput parsing and schema validation of transaction batches with instant execution feedback.
- **Deterministic Rules Engine**: High-speed evaluation of transaction ledgers against active statutory policies:
  - `RULE-AML-001`: BSA Currency Transaction Report (CTR) threshold ($10,000 USD).
  - `RULE-SANCTIONS-001`: OFAC embargoed jurisdiction screening (PRK, IRN, SYR, CUB, RUS).
  - `RULE-KYC-001`: Customer Due Diligence (CDD) unverified customer transaction limits.
  - `RULE-STRUCTURING-001`: Anti-structuring / smurfing boundary detection ($9,000 - $9,999 USD).
  - `RULE-TIMING-001`: Off-hours high-risk wire transfer protocol (01:00 - 05:00 UTC).
- **Violations Triage Desk**: Real-time filtering by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), status (`OPEN`, `UNDER_REVIEW`, `RESOLVED`), and keyword search with a slide-over inspection drawer and auditor notes logging.
- **Institutional PDF Audit Reports**: One-click generation of institutional-grade compliance PDF audit reports built with ReportLab, featuring executive KPIs, policy breach tables, and auditor sign-off signature blocks.
- **Restrained B2B SaaS UI**: Designed with Linear/Stripe ops tool restraint — slate/charcoal palette, crisp typography, clean SVG icons (zero emoji gimmicks), and data-dense layout.

---

## 3. Tech Architecture

```
[ React SPA Frontend ]
       │
       │  (REST API with JWT + Tenant Context)
       ▼
[ FastAPI Backend ] ──► [ Multi-Tenant Scoping ] ──► [ PostgreSQL / SQLite ]
       │
       ├─► [ CSV Ingestion & Schema Validator ]
       ├─► [ Deterministic Rules Engine ]
       └─► [ ReportLab PDF Engine ]
```

### Ingestion → Validation → Reporting Flow
1. **Ingestion**: Uploaded CSV files stream through `app.services.ingestion`, validating required fields (`transaction_id`, `account_id`, `amount`) and casting timestamps and currencies.
2. **Deterministic Evaluation**: Batch records pass through `RulesEngine` where every active rule evaluates condition sets, returning structured violation objects.
3. **Database Scoping**: Records and violations are committed in a single transaction with explicit `tenant_id` foreign keys.
4. **Reporting**: `generate_compliance_pdf_report` queries tenant metrics and violation ledgers, rendering a binary PDF output.

### Multi-Tenancy & RBAC Enforcement
- Every database entity (`User`, `DatasetUpload`, `TransactionRecord`, `Violation`) contains a mandatory `tenant_id` foreign key.
- API endpoints invoke `get_current_user` dependency, extracting the user from the verified JWT sub.
- Every database query explicitly scopes filters with `.filter(Entity.tenant_id == current_user.tenant_id)` preventing cross-tenant data leaks.
- Role checks (`require_roles(["admin"])`) enforce permission guards on sensitive endpoints like rule toggling and user registration.

---

## 4. How to Run Locally

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Node.js v18+ & npm 9+
- PostgreSQL (Optional, SQLite is configured as zero-setup default)

### Setup Steps

#### 1. Clone & Setup Backend
```bash
# Navigate to project root
cd "Compliance Platform"

# Create and activate Python virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

#### 2. Environment Variables Configuration
Copy `.env.example` to `.env` in the `backend/` directory or root:
```env
APP_NAME="Apex Compliance Engine"
ENVIRONMENT="development"

# Database Connection (Default: SQLite zero-setup)
DATABASE_URL="sqlite:///./compliance.db"
# For PostgreSQL: postgresql://postgres:password@localhost:5432/compliance_db

SECRET_KEY="compliance-secure-dev-key-a89f31c4e976b42d"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=480
CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
```

#### 3. Run Database Migrations & Seed Data
```bash
# Run Alembic migrations
alembic upgrade head

# Seed demo tenant, users, rules, and sample transaction CSV
python backend/seed.py
```

#### 4. Start Backend Server
```bash
# Start FastAPI backend server on Port 8000
python -m uvicorn app.main:app --reload --port 8000 --app-dir backend
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

#### 5. Install & Start Frontend Server
Open a new terminal tab/window:
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server on Port 5173
npm run dev
```
- Frontend Web App: `http://localhost:5173`

---

## 5. How to Use It (User Walkthrough)

### 1. Logging In
- Open `http://localhost:5173` in your browser.
- Use pre-seeded demo credentials or click **"Quick Demo Logins"**:
  - **Lead Admin**: `admin@meridian.com` / `admin123`
  - **Compliance Officer**: `compliance@meridian.com` / `officer123`
- Or switch to **"Create Organization"** to register a new tenant company.

### 2. Viewing Executive Telemetry (Dashboard)
- Upon logging in, you land on the **Dashboard**.
- **Compliance Health Rate**: Displays adherence percentage (target >95%).
- **Violation Severity Distribution**: Bar chart showing Critical, High, Medium, and Low risk weightings.
- **Rule Distribution Ranking**: Identifies which regulatory rules are most frequently breached.
- **Pending Violations Queue**: Quick preview of unhandled compliance flags.

### 3. Ingesting Transaction CSV Files (Upload)
- Click **"Ingestion & Upload"** in the sidebar.
- Drag & drop a transaction CSV file onto the dropzone or click to select a file.
- Click **"Download Sample CSV"** to test with the provided multi-case sample dataset.
- Upon upload, the platform automatically parses records, evaluates active compliance rules, displays summary counts, and logs the file into **Batch Ingestion History**.

### 4. Triaging & Resolving Violations (Violations Triage)
- Click **"Violations Triage"** in the sidebar.
- Filter findings by **Severity** (`CRITICAL`, `HIGH`, etc.), **Status** (`OPEN`, `UNDER_REVIEW`, `RESOLVED`), or type keywords in the search bar.
- Click any table row or the **"Triage"** button to open the **Slide-over Inspection Drawer**.
- Review the complete transaction metadata (counterparty, country, KYC status, transfer type, amount).
- Change status (e.g. from `OPEN` to `RESOLVED`), input auditor notes in the audit trail field, and click **"Save Triage Changes"**.

### 5. Generating & Downloading Compliance PDF Audit Reports (Reports)
- Click **"Audit Reports (PDF)"** in the sidebar.
- Review the audit parameters and legal entity scope.
- Click **"Download Compliance PDF"**.
- A compiled, institutional-grade PDF report will download directly to your machine containing executive summary metrics, policy breach ledgers, and auditor sign-off blocks.

### 6. Managing Policy Thresholds (Rules Repository)
- Click **"Rules Repository"** in the sidebar.
- Inspect active statutory policies, parameters, and regulatory references.
- Admin users can click the **Active / Disabled** toggle button to enable or disable specific rules for the tenant.

---

## 6. Deployment Notes

### Production Architecture
- **Frontend SPA**: Deployed to **Vercel** or Netlify.
- **Backend API**: Deployed to **Render**, Railway, or AWS ECS.
- **Database**: Managed **PostgreSQL** (e.g. Render Postgres, AWS RDS).

### Environment Variables Required

#### Frontend (Vercel)
- `VITE_API_URL`: Public HTTPS URL of the backend API (e.g. `https://apex-compliance-api.onrender.com/api`)

#### Backend (Render / Cloud Host)
- `DATABASE_URL`: PostgreSQL connection string (e.g. `postgresql://user:pass@ep-xyz.postgres.database.azure.com/compliance_db`)
- `SECRET_KEY`: High-entropy random key for JWT signing
- `ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `480`
- `CORS_ORIGINS`: Allowed production origins (e.g. `https://apex-compliance.vercel.app`)
- `ENVIRONMENT`: `production`

---

## 7. Known Limitations (V1 Scope)

- **Deterministic Rules Engine Only**: V1 relies strictly on deterministic statutory thresholds and boolean rules. Machine learning anomaly detection and probabilistic clustering are omitted from V1.
- **Single-Country Regulatory Framework**: Rules default to US single-country regulatory frameworks (BSA, FinCEN, OFAC). Multi-jurisdictional cross-border tax mapping (FATCA/CRS) is not included in V1.
- **No Automated Email Notifications**: Status changes and critical flags update the live dashboard telemetry; external SMTP email alerts and Webhooks are not included in V1.
- **No Billing / Subscription Module**: Tenant onboarding is provided for multi-tenant isolation, without integrated payment processors or subscription tiers.
