from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.schemas.budget import BudgetCreate, BudgetResponse
from app.services import budget_service
from app.api.deps import get_optional_current_user
from app.models.user import User

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.get("", response_model=List[BudgetResponse])
@router.get("/", response_model=List[BudgetResponse])
def read_budgets(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """List budgets with spent amount, remaining balance, and warning status."""
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year
    user_id = current_user.id if current_user else None

    return budget_service.get_budgets(
        db=db,
        user_id=user_id,
        month=target_month,
        year=target_year
    )

@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def set_budget(
    budget_in: BudgetCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Create or update a category budget limit for a specific month/year."""
    user_id = current_user.id if current_user else None
    return budget_service.create_or_update_budget(
        db=db,
        budget_in=budget_in,
        user_id=user_id
    )

@router.delete("/{budget_id}")
def remove_budget(
    budget_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Delete a budget entry by ID."""
    user_id = current_user.id if current_user else None
    success = budget_service.delete_budget(db=db, budget_id=budget_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with ID {budget_id} not found."
        )
    return {"message": f"Budget with ID {budget_id} deleted."}
