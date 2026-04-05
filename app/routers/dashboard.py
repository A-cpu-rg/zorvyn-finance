from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_analyst_or_above
from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    _: User = Depends(require_analyst_or_above),  # Analyst + Admin only
    db: Session = Depends(get_db),
):
    """
    [Analyst & Admin] Full dashboard summary including:
    - Total income, expenses, net balance
    - Per-category breakdowns
    - Last 10 recent transactions
    - Monthly trends for the past 12 months
    """
    return get_dashboard_summary(db)
