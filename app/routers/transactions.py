from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin, require_any_role
from app.database import get_db
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilter,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)
from app.services.transaction import (
    create_transaction,
    delete_transaction,
    get_transaction_by_id,
    get_transactions,
    search_transactions,
    update_transaction,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=TransactionListResponse)
def list_transactions(
    type: TransactionType | None = Query(None, description="Filter by income or expense"),
    category: str | None = Query(None, description="Filter by category name (partial match)"),
    date_from: date | None = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="Filter to date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_any_role),  # Viewer, Analyst, Admin — all can read
    db: Session = Depends(get_db),
):
    """
    [All roles] List financial records with optional filters.
    Supports filtering by type, category, and date range with pagination.
    """
    filters = TransactionFilter(
        type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return get_transactions(filters, db)


@router.get("/search", response_model=TransactionListResponse)
def search(
    q: str = Query(..., min_length=1, max_length=200, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_any_role),  # All roles can search
    db: Session = Depends(get_db),
):
    """
    [All roles] Full-text search across transaction category and notes.
    Uses case-insensitive partial matching.
    """
    return search_transactions(query=q, page=page, page_size=page_size, db=db)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    _: User = Depends(require_any_role),  # All roles can read individual records
    db: Session = Depends(get_db),
):
    """[All roles] Get a single transaction by ID."""
    return get_transaction_by_id(transaction_id, db)


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_new_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(require_admin),  # Only Admin can create
    db: Session = Depends(get_db),
):
    """
    [Admin only] Create a new financial record.
    Amount must be positive. Date cannot be in the future.
    """
    return create_transaction(payload, current_user, db)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_existing_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    _: User = Depends(require_admin),  # Only Admin can update
    db: Session = Depends(get_db),
):
    """[Admin only] Update fields of an existing transaction."""
    return update_transaction(transaction_id, payload, db)


@router.delete("/{transaction_id}")
def delete_existing_transaction(
    transaction_id: int,
    _: User = Depends(require_admin),  # Only Admin can delete
    db: Session = Depends(get_db),
):
    """[Admin only] Soft-delete a transaction (data is preserved, just hidden)."""
    return delete_transaction(transaction_id, db)
