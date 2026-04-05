from pydantic import BaseModel

from app.schemas.transaction import TransactionResponse


class CategoryTotal(BaseModel):
    category: str
    total: float
    count: int


class MonthlyTrend(BaseModel):
    year: int
    month: int
    income: float
    expense: float
    net: float


class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    total_transactions: int
    income_transactions: int
    expense_transactions: int
    category_totals: list[CategoryTotal]
    recent_transactions: list[TransactionResponse]
    monthly_trends: list[MonthlyTrend]
