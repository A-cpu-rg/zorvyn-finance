from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.transaction import TransactionType


# ── Request Schemas ──────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be positive")
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=100, examples=["Salary"])
    date: date
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category cannot be blank")
        return v.strip().title()

    @field_validator("date")
    @classmethod
    def date_not_in_future(cls, v: date) -> date:
        from datetime import date as date_type
        if v > date_type.today():
            raise ValueError("Transaction date cannot be in the future")
        return v


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("category")
    @classmethod
    def category_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip().title()
        return v


# ── Response Schemas ─────────────────────────────────────────────────────────

class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    transactions: list[TransactionResponse]


# ── Filter Schema ─────────────────────────────────────────────────────────────

class TransactionFilter(BaseModel):
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


# ── Search Schema ─────────────────────────────────────────────────────────────

class TransactionSearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=200, description="Search term")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
