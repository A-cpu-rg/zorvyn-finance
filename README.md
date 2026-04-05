# Zorvyn Finance Dashboard — Backend API

A clean, production-minded REST API for a finance dashboard system with role-based access control, financial record management, and analytics. Built as part of the Zorvyn Backend Developer Intern screening assessment.

---

## Tech Stack (Industry-Level Upgrade)

| Layer | Choice | Reason |
|---|---|---|
| Framework | **FastAPI** | Auto-generates Swagger docs, async-ready, fast |
| Database | **PostgreSQL + SQLAlchemy ORM** | Production-grade relational database with connection pooling |
| Migrations | **Alembic** | Version-controllable database schema management |
| Auth | **JWT (python-jose)** | Stateless, industry-standard token auth |
| Validation | **Pydantic v2** | Built into FastAPI; catches all invalid inputs early |
| Security | **bcrypt (passlib)** | Secure, production-grade hashing |
| Rate Limiting| **SlowAPI** | In-memory API request restriction, preventing abuse |

---

## Key Features Added for Industry-Level
- **PostgreSQL Database:** Upgraded from SQLite to properly pooled PostgreSQL connection.
- **Alembic Migrations:** Production-ready schema migration tracking.
- **Structured Middleware:** Request-ID generation (`X-Request-ID`) and robust request/response timing logging.
- **Rate Limiting:** Enforces 100 requests/minute by default (10 req/min for auth).
- **Global Exception Parsing:** Formatted error responses (`error_code`, `request_id`).
- **Search Capability:** Perform full-text, partial matches across transaction tags & notes.
- **Comprehensive DB Seeding:** Auto-creates initial realistic users and dashboard metrics.

---

## Project Structure

```
finance-backend/
├── app/
│   ├── main.py               # FastAPI app, routers, middleware, exception handlers
│   ├── config.py             # App-level config settings (loaded from .env)
│   ├── database.py           # Database engine & connection pool logic
│   ├── models/               # SQLAlchemy Models: User, Transaction
│   ├── schemas/              # Pydantic Request/Response shapes
│   ├── core/
│   │   ├── middleware.py     # RequestID, Logging middleware
│   │   ├── exceptions.py     # Custom application exceptions for generic handling
│   │   ├── security.py       # JWT encode/decode, bcrypt hash/verify
│   │   └── dependencies.py   # FastAPI deps: get_current_user, require_admin, etc.
│   ├── services/             # Core business logic: CRUD ops, Dashboard aggregation
│   └── routers/              # API endpoints organized by entity
├── alembic/                  # Database migration configuration
├── scripts/
│   └── seed.py               # DB pre-population script
├── run.py                    # Convenience entrypoint configuration
├── requirements.txt
├── .env / .env.example       # API environment setups
└── README.md
```

---

## Setup & Running

### 1. Requirements
Ensure **PostgreSQL 14+** is installed and running on your device. Ensure you have **Python 3.11**.

### 2. Clone and install dependencies

```bash
git clone <your-repo-url>
cd finance-backend

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Database Environment

```bash
cp .env.example .env
```
Ensure your database named `finance_db` exists on Postgres.
Update the `.env` if your local Postgres instance requires authentication.
```bash
DATABASE_URL=postgresql://localhost:5432/finance_db
```

### 4. Create Tables & Seed Data

```bash
# Run Alembic migrations
alembic upgrade head

# Pre-populate data (Users & 30 dummy transactions)
python scripts/seed.py
```
> ***Pre-seeded Users (all share password `admin123`, `analyst123`, `viewer123` respectively)***
> - Admin: `admin@zorvyn.com`
> - Analyst: `analyst@zorvyn.com`
> - Viewer: `viewer@zorvyn.com`

### 5. Run the server

```bash
python run.py
```

Server starts at: **http://localhost:8000**

---

## Explore the API

- **Swagger UI**: http://localhost:8000/docs ← interactive, test everything here
- **Health check**: http://localhost:8000/health

### Getting Started (First Steps)

```bash
# 1. Login with the seeded Admin User
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@zorvyn.com", "password": "admin123"}'

# 2. Extract access_token
export TOKEN="<paste access_token here>"

# 3. Create a transaction
curl -X POST http://localhost:8000/api/v1/transactions/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 50000, "type": "income", "category": "Salary", "date": "2026-04-01"}'

# 4. View dashboard (Analyst and up)
curl http://localhost:8000/api/v1/dashboard/summary \
  -H "Authorization: Bearer $TOKEN"

# 5. Search transactions
curl "http://localhost:8000/api/v1/transactions/search?q=Salary" \
  -H "Authorization: Bearer $TOKEN"
```



## Author

**Abhishek Meena**
abhishek.m23csai@nst.rishihood.edu.in
Backend Developer Intern - Zorvyn Assessment
