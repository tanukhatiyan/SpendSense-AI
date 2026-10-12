from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.services import expense_service
from app.api.deps import get_optional_current_user
from app.models.user import User

router = APIRouter(tags=["Expenses"])

@router.get("", response_model=List[ExpenseResponse])
@router.get("/", response_model=List[ExpenseResponse])
def read_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by income or expense"),
    search: Optional[str] = Query(None, description="Search transaction title"),
    start_date: Optional[date] = Query(None, description="Filter from start date"),
    end_date: Optional[date] = Query(None, description="Filter until end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve transactions, optionally filtered and paginated."""
    user_id = current_user.id if current_user else None
    return expense_service.get_expenses(
        db=db,
        user_id=user_id,
        category=category,
        type=type,
        search=search,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

@router.get("/totals")
def read_financial_totals(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Get calculated total income, total expenses, net balance, and count."""
    user_id = current_user.id if current_user else None
    return expense_service.get_financial_totals(db=db, user_id=user_id)

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_new_expense(
    expense_in: ExpenseCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Create and persist a new transaction."""
    user_id = current_user.id if current_user else None
    return expense_service.create_expense(db=db, expense_in=expense_in, user_id=user_id)

@router.get("/{expense_id}", response_model=ExpenseResponse)
def read_single_expense(
    expense_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a single transaction by ID."""
    user_id = current_user.id if current_user else None
    db_expense = expense_service.get_expense_by_id(db=db, expense_id=expense_id, user_id=user_id)
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found."
        )
    return db_expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_existing_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing transaction."""
    user_id = current_user.id if current_user else None
    updated = expense_service.update_expense(
        db=db,
        expense_id=expense_id,
        expense_in=expense_in,
        user_id=user_id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found."
        )
    return updated

@router.delete("/{expense_id}")
def delete_existing_expense(
    expense_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Delete a transaction by ID."""
    user_id = current_user.id if current_user else None
    success = expense_service.delete_expense(
        db=db,
        expense_id=expense_id,
        user_id=user_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found."
        )
    return {"message": f"Expense with ID {expense_id} has been deleted."}
