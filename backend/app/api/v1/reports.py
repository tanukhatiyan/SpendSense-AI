from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.db.session import get_db
from app.schemas.report import FinanceSummary
from app.services import report_service
from app.api.deps import get_optional_current_user
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/summary", response_model=FinanceSummary)
def get_summary(
    start_date: Optional[date] = Query(None, description="Start date for summary"),
    end_date: Optional[date] = Query(None, description="End date for summary"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve financial summary including category distribution and monthly trends."""
    user_id = current_user.id if current_user else None
    return report_service.get_finance_summary(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )

@router.get("/export-csv")
def export_csv(
    start_date: Optional[date] = Query(None, description="Start date for export"),
    end_date: Optional[date] = Query(None, description="End date for export"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Export transactions to a downloadable RFC 4180 CSV file."""
    user_id = current_user.id if current_user else None
    csv_content = report_service.generate_expenses_csv(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    filename = f"spendsense_export_{date.today().isoformat()}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
