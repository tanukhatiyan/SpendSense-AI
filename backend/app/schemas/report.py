from pydantic import BaseModel
from typing import List

class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int
    percentage: float

class MonthlySummary(BaseModel):
    month: int
    year: int
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int

class FinanceSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int
    category_breakdown: List[CategoryBreakdown]
    monthly_trend: List[MonthlySummary]
