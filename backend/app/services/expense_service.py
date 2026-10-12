from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate

def get_expenses(
    db: Session,
    user_id: Optional[int] = None,
    category: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Expense]:
    """Retrieve filtered and paginated expenses for an authorized user."""
    query = db.query(Expense)

    if user_id is not None:
        query = query.filter(Expense.user_id == user_id)
    else:
        query = query.filter(Expense.user_id.is_(None))
    if category:
        query = query.filter(Expense.category.ilike(f"%{category.strip()}%"))
    if type:
        query = query.filter(Expense.type == type.strip().lower())
    if search:
        query = query.filter(Expense.title.ilike(f"%{search.strip()}%"))
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)

    return query.order_by(Expense.date.desc(), Expense.id.desc()).offset(skip).limit(limit).all()

def count_expenses(
    db: Session,
    user_id: Optional[int] = None,
    category: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> int:
    """Return total count matching filter parameters."""
    query = db.query(Expense)
    if user_id is not None:
        query = query.filter(Expense.user_id == user_id)
    else:
        query = query.filter(Expense.user_id.is_(None))
    if category:
        query = query.filter(Expense.category.ilike(f"%{category.strip()}%"))
    if type:
        query = query.filter(Expense.type == type.strip().lower())
    if search:
        query = query.filter(Expense.title.ilike(f"%{search.strip()}%"))
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    return query.count()

def get_expense_by_id(db: Session, expense_id: int, user_id: Optional[int] = None) -> Optional[Expense]:
    """Find a specific expense by ID, guaranteeing ownership matches user_id if supplied."""
    query = db.query(Expense).filter(Expense.id == expense_id)
    if user_id is not None:
        query = query.filter(Expense.user_id == user_id)
    else:
        query = query.filter(Expense.user_id.is_(None))
    return query.first()

def create_expense(db: Session, expense_in: ExpenseCreate, user_id: Optional[int] = None) -> Expense:
    """Persist a new transaction linked to the authorized user."""
    expense_data = expense_in.model_dump()
    if expense_data.get("date") is None:
        expense_data["date"] = date.today()

    db_expense = Expense(
        title=expense_data["title"],
        amount=round(expense_data["amount"], 2),
        category=expense_data["category"],
        type=expense_data["type"],
        date=expense_data["date"],
        notes=expense_data.get("notes"),
        user_id=user_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def update_expense(
    db: Session,
    expense_id: int,
    expense_in: ExpenseUpdate,
    user_id: Optional[int] = None
) -> Optional[Expense]:
    """Update an existing transaction record, verifying ownership."""
    db_expense = get_expense_by_id(db, expense_id, user_id)
    if not db_expense:
        return None

    update_data = expense_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "amount" and value is not None:
            value = round(value, 2)
        setattr(db_expense, field, value)

    db.commit()
    db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int, user_id: Optional[int] = None) -> bool:
    """Delete a transaction if found and authorized."""
    db_expense = get_expense_by_id(db, expense_id, user_id)
    if not db_expense:
        return False
    db.delete(db_expense)
    db.commit()
    return True

def get_financial_totals(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
    """Calculate precise financial metrics (Income, Expenses, Net Balance, Count)."""
    query = db.query(Expense)
    if user_id is not None:
        query = query.filter(Expense.user_id == user_id)
    else:
        query = query.filter(Expense.user_id.is_(None))

    all_records = query.all()
    total_income = Decimal("0.00")
    total_expenses = Decimal("0.00")

    for item in all_records:
        item_amount = Decimal(str(round(item.amount, 2)))
        if item.type == "income":
            total_income += item_amount
        elif item.type == "expense":
            total_expenses += item_amount

    net_balance = total_income - total_expenses

    return {
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "current_balance": float(net_balance),
        "transaction_count": len(all_records),
    }
