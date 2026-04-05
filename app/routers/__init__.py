from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.transactions import router as transactions_router
from app.routers.users import router as users_router

__all__ = ["auth_router", "users_router", "transactions_router", "dashboard_router"]
