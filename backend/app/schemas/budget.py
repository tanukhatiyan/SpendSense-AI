from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime

class BudgetBase(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    monthly_limit: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)

    @field_validator("category")
    @classmethod
    def clean_category(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Category cannot be empty")
        return trimmed

    @field_validator("monthly_limit")
    @classmethod
    def round_limit(cls, v: float) -> float:
        return round(v, 2)

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    monthly_limit: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = Field(None, ge=2000, le=2100)

    @field_validator("monthly_limit")
    @classmethod
    def round_limit(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            return round(v, 2)
        return v

class BudgetResponse(BudgetBase):
    id: int
    user_id: Optional[int] = None
    spent: float = 0.0
    remaining: float = 0.0
    percentage: float = 0.0
    status: Literal["normal", "warning", "exceeded"] = "normal"
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
