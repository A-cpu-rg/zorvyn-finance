import logging

from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilter,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)

logger = logging.getLogger("zorvyn.service.transaction")


def create_transaction(
    payload: TransactionCreate, current_user: User, db: Session
) -> TransactionResponse:
    transaction = Transaction(
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes,
        created_by=current_user.id,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    logger.info("Transaction #%d created by user #%d", transaction.id, current_user.id)
    return TransactionResponse.model_validate(transaction)


def get_transactions(
    filters: TransactionFilter, db: Session
) -> TransactionListResponse:
    conditions = [Transaction.is_deleted == False]  # noqa: E712

    if filters.type:
        conditions.append(Transaction.type == filters.type)
    if filters.category:
        conditions.append(
            Transaction.category.ilike(f"%{filters.category}%")
        )
    if filters.date_from:
        conditions.append(Transaction.date >= filters.date_from)
    if filters.date_to:
        conditions.append(Transaction.date <= filters.date_to)

    query = db.query(Transaction).filter(and_(*conditions)).order_by(
        Transaction.date.desc(), Transaction.created_at.desc()
    )

    total = query.count()
    records = (
        query.offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
        .all()
    )

    return TransactionListResponse(
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        transactions=[TransactionResponse.model_validate(r) for r in records],
    )


def get_transaction_by_id(transaction_id: int, db: Session) -> TransactionResponse:
    record = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False,  # noqa: E712
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    return TransactionResponse.model_validate(record)


def update_transaction(
    transaction_id: int, payload: TransactionUpdate, db: Session
) -> TransactionResponse:
    record = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False,  # noqa: E712
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    logger.info("Transaction #%d updated", transaction_id)
    return TransactionResponse.model_validate(record)


def delete_transaction(transaction_id: int, db: Session) -> dict:
    """Soft delete."""
    record = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False,  # noqa: E712
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    record.is_deleted = True
    db.commit()
    logger.info("Transaction #%d soft-deleted", transaction_id)
    return {"message": f"Transaction #{transaction_id} deleted successfully"}


def search_transactions(
    query: str, page: int, page_size: int, db: Session
) -> TransactionListResponse:
    """
    Full-text search across transaction category and notes fields.
    Uses case-insensitive ILIKE matching (works on both SQLite and PostgreSQL).
    """
    search_term = f"%{query.strip()}%"
    conditions = [
        Transaction.is_deleted == False,  # noqa: E712
        or_(
            Transaction.category.ilike(search_term),
            Transaction.notes.ilike(search_term),
        ),
    ]

    db_query = db.query(Transaction).filter(and_(*conditions)).order_by(
        Transaction.date.desc(), Transaction.created_at.desc()
    )

    total = db_query.count()
    records = (
        db_query.offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    logger.info("Search '%s' returned %d results", query, total)
    return TransactionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        transactions=[TransactionResponse.model_validate(r) for r in records],
    )
