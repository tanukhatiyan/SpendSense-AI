from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, Optional
from datetime import date as dt_date, datetime

class ExpenseBase(BaseModel):
    title: str = Field(..., description="Transaction title, e.g. Grocery, Salary")
    amount: float = Field(..., gt=0, description="Amount strictly greater than zero")
    category: str = Field(..., description="Category, e.g. Food, Transport, Rent, Salary")
    type: Literal["income", "expense"] = Field(..., description="Type must be either income or expense")
    date: Optional[dt_date] = Field(default_factory=dt_date.today, description="Transaction date")
    notes: Optional[str] = Field(None, description="Optional transaction notes")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Title cannot be empty or purely whitespace")
        return trimmed

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Category cannot be empty")
        return trimmed

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float) -> float:
        return round(v, 2)

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    type: Optional[Literal["income", "expense"]] = None
    date: Optional[dt_date] = None
    notes: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Title cannot be empty")
            return trimmed
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Category cannot be empty")
            return trimmed
        return v

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            return round(v, 2)
        return v

class ExpenseResponse(ExpenseBase):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
