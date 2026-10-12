from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import List, Optional
from datetime import date
from decimal import Decimal
from app.models.budget import Budget
from app.models.expense import Expense
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse

def get_category_spent(
    db: Session,
    category: str,
    month: int,
    year: int,
    user_id: Optional[int] = None
) -> float:
    """Calculate total expense spending for a category in a specific month and year."""
    query = db.query(Expense).filter(
        Expense.type == "expense",
        Expense.category.ilike(category.strip()),
        extract("month", Expense.date) == month,
        extract("year", Expense.date) == year
    )
    if user_id is not None:
        query = query.filter(Expense.user_id == user_id)
    else:
        query = query.filter(Expense.user_id.is_(None))

    total = Decimal("0.00")
    for exp in query.all():
        total += Decimal(str(round(exp.amount, 2)))
    return float(total)

def enrich_budget_response(db: Session, budget: Budget) -> BudgetResponse:
    """Calculate spent, remaining, percentage, and warning status for a budget."""
    spent = get_category_spent(
        db=db,
        category=budget.category,
        month=budget.month,
        year=budget.year,
        user_id=budget.user_id
    )
    limit = budget.monthly_limit
    remaining = max(0.0, round(limit - spent, 2))
    percentage = round((spent / limit) * 100, 1) if limit > 0 else 0.0

    if percentage >= 100.0:
        status = "exceeded"
    elif percentage >= 80.0:
        status = "warning"
    else:
        status = "normal"

    return BudgetResponse(
        id=budget.id,
        category=budget.category,
        monthly_limit=budget.monthly_limit,
        month=budget.month,
        year=budget.year,
        user_id=budget.user_id,
        spent=spent,
        remaining=remaining,
        percentage=percentage,
        status=status,
        created_at=budget.created_at
    )

def get_budgets(
    db: Session,
    user_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> List[BudgetResponse]:
    """Retrieve all budgets with computed utilization metrics."""
    query = db.query(Budget)
    if user_id is not None:
        query = query.filter(Budget.user_id == user_id)
    else:
        query = query.filter(Budget.user_id.is_(None))
    if month is not None:
        query = query.filter(Budget.month == month)
    if year is not None:
        query = query.filter(Budget.year == year)

    budgets = query.order_by(Budget.category.asc()).all()
    return [enrich_budget_response(db, b) for b in budgets]

def create_or_update_budget(
    db: Session,
    budget_in: BudgetCreate,
    user_id: Optional[int] = None
) -> BudgetResponse:
    """Create a new budget or update limit if one already exists for category/month/year."""
    clean_cat = budget_in.category.strip()
    existing = db.query(Budget).filter(
        Budget.category.ilike(clean_cat),
        Budget.month == budget_in.month,
        Budget.year == budget_in.year,
    )
    if user_id is not None:
        existing = existing.filter(Budget.user_id == user_id)
    else:
        existing = existing.filter(Budget.user_id.is_(None))
    
    budget = existing.first()
    if budget:
        budget.monthly_limit = round(budget_in.monthly_limit, 2)
        budget.category = clean_cat
    else:
        budget = Budget(
            category=clean_cat,
            monthly_limit=round(budget_in.monthly_limit, 2),
            month=budget_in.month,
            year=budget_in.year,
            user_id=user_id
        )
        db.add(budget)

    db.commit()
    db.refresh(budget)
    return enrich_budget_response(db, budget)

def delete_budget(db: Session, budget_id: int, user_id: Optional[int] = None) -> bool:
    """Delete a budget entry by ID with authorization verification."""
    query = db.query(Budget).filter(Budget.id == budget_id)
    if user_id is not None:
        query = query.filter(Budget.user_id == user_id)
    else:
        query = query.filter(Budget.user_id.is_(None))
    
    budget = query.first()
    if not budget:
        return False
    db.delete(budget)
    db.commit()
    return True
