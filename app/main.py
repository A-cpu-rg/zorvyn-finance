import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.core.exceptions import AppException
from app.core.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.database import Base, engine
from app.routers import auth_router, dashboard_router, transactions_router, users_router

# Import models so SQLAlchemy discovers them before create_all
import app.models  # noqa: F401

logger = logging.getLogger("zorvyn")

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all database tables on startup."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created / verified")
    logger.info("Zorvyn Finance API started on http://0.0.0.0:8000")
    yield
    logger.info("Zorvyn Finance API shutting down")


app = FastAPI(
    title="Zorvyn Finance Dashboard API",
    description=(
        "Backend API for the Zorvyn Finance Dashboard System.\n\n"
        "## Roles & Permissions\n"
        "| Role | View Records | View Dashboard | Create/Edit/Delete Records | Manage Users |\n"
        "|------|-------------|---------------|---------------------------|-------------|\n"
        "| **Viewer** | ✅ | ❌ | ❌ | ❌ |\n"
        "| **Analyst** | ✅ | ✅ | ❌ | ❌ |\n"
        "| **Admin** | ✅ | ✅ | ✅ | ✅ |\n\n"
        "## Getting Started\n"
        "1. Register your first account via `POST /api/v1/auth/register` "
        "(automatically granted Admin role).\n"
        "2. Log in via `POST /api/v1/auth/login` to receive a Bearer token.\n"
        "3. Click **Authorize** above and paste your token to test protected endpoints.\n\n"
        "## Features\n"
        "- 🔐 JWT authentication with bcrypt password hashing\n"
        "- 🛡️ Role-based access control (Viewer / Analyst / Admin)\n"
        "- 📊 Dashboard analytics with category & monthly trends\n"
        "- 🔍 Full-text search across transactions\n"
        "- ⚡ Rate limiting (100 req/min default, 10 req/min for auth)\n"
        "- 📝 Structured request logging with X-Request-ID tracing\n"
        "- 🗑️ Soft deletes for audit trail preservation\n"
        "- 📄 Pagination on all list endpoints\n"
    ),
    version="1.0.0",
    contact={"name": "Abhishek Meena", "email": "abhishek.m23csai@nst.rishihood.edu.in"},
    lifespan=lifespan,
)

# Attach rate limiter to app state
app.state.limiter = limiter

# ── Middleware (order matters — outermost runs first) ─────────────────────────
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception handlers ────────────────────────────────────────────────────────

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Return structured error responses for custom exceptions."""
    request_id = getattr(request.state, "request_id", None)
    body = {"detail": exc.detail, "error_code": exc.error_code}
    if request_id:
        body["request_id"] = request_id
    return JSONResponse(status_code=exc.status_code, content=body)


app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.exception("Unhandled exception [%s]: %s", request_id, exc)
    body = {"detail": "An unexpected error occurred. Please try again."}
    if request_id:
        body["request_id"] = request_id
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=body,
    )


# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)
app.include_router(transactions_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    """Simple liveness probe — useful for deployment monitoring."""
    return {"status": "ok", "service": "Zorvyn Finance API", "version": "1.0.0"}


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to the Zorvyn Finance Dashboard API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
