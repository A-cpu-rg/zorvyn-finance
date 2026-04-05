from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.dashboard import CategoryTotal, DashboardSummary, MonthlyTrend
from app.schemas.transaction import TransactionResponse


def get_dashboard_summary(db: Session) -> DashboardSummary:
    """
    Computes all dashboard metrics in a single efficient query pass.
    Uses Python-level aggregation after a single DB fetch to keep
    the implementation clear and maintainable.
    """
    records = (
        db.query(Transaction)
        .filter(Transaction.is_deleted == False)  # noqa: E712
        .order_by(Transaction.date.desc())
        .all()
    )

    total_income = 0.0
    total_expense = 0.0
    income_count = 0
    expense_count = 0
    category_map: dict[str, dict] = defaultdict(lambda: {"total": 0.0, "count": 0})
    monthly_map: dict[tuple, dict] = defaultdict(
        lambda: {"income": 0.0, "expense": 0.0}
    )

    for r in records:
        if r.type == TransactionType.INCOME:
            total_income += r.amount
            income_count += 1
        else:
            total_expense += r.amount
            expense_count += 1

        category_map[r.category]["total"] += r.amount
        category_map[r.category]["count"] += 1

        key = (r.date.year, r.date.month)
        if r.type == TransactionType.INCOME:
            monthly_map[key]["income"] += r.amount
        else:
            monthly_map[key]["expense"] += r.amount

    category_totals = [
        CategoryTotal(category=cat, total=round(data["total"], 2), count=data["count"])
        for cat, data in sorted(category_map.items(), key=lambda x: -x[1]["total"])
    ]

    monthly_trends = [
        MonthlyTrend(
            year=year,
            month=month,
            income=round(data["income"], 2),
            expense=round(data["expense"], 2),
            net=round(data["income"] - data["expense"], 2),
        )
        for (year, month), data in sorted(monthly_map.items(), reverse=True)
    ][:12]  # last 12 months

    recent = records[:10]

    return DashboardSummary(
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        net_balance=round(total_income - total_expense, 2),
        total_transactions=len(records),
        income_transactions=income_count,
        expense_transactions=expense_count,
        category_totals=category_totals,
        recent_transactions=[TransactionResponse.model_validate(r) for r in recent],
        monthly_trends=monthly_trends,
    )
