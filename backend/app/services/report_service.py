from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
import io
import csv
from app.models.expense import Expense
from app.schemas.report import FinanceSummary, CategoryBreakdown, MonthlySummary

def get_finance_summary(
    db: Session,
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> FinanceSummary:
    """Generate comprehensive financial summary with category breakdown and monthly trends."""
    query = db.query(Expense)
    if user_id is not None:
        query = query.filter(Expense.user_id == user_id)
    else:
        query = query.filter(Expense.user_id.is_(None))
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)

    records = query.all()

    total_income = Decimal("0.00")
    total_expenses = Decimal("0.00")
    category_totals: Dict[str, Decimal] = {}
    category_counts: Dict[str, int] = {}
    monthly_data: Dict[str, Dict[str, Any]] = {}

    for item in records:
        amt = Decimal(str(round(item.amount, 2)))
        m_key = f"{item.date.year}-{item.date.month:02d}"

        if m_key not in monthly_data:
            monthly_data[m_key] = {
                "month": item.date.month,
                "year": item.date.year,
                "income": Decimal("0.00"),
                "expense": Decimal("0.00"),
                "count": 0,
            }
        monthly_data[m_key]["count"] += 1

        if item.type == "income":
            total_income += amt
            monthly_data[m_key]["income"] += amt
        elif item.type == "expense":
            total_expenses += amt
            monthly_data[m_key]["expense"] += amt
            cat = item.category.strip()
            category_totals[cat] = category_totals.get(cat, Decimal("0.00")) + amt
            category_counts[cat] = category_counts.get(cat, 0) + 1

    net_balance = total_income - total_expenses

    # Category breakdown calculations
    breakdown: List[CategoryBreakdown] = []
    for cat, cat_tot in category_totals.items():
        pct = float(round((cat_tot / total_expenses * 100), 1)) if total_expenses > 0 else 0.0
        breakdown.append(
            CategoryBreakdown(
                category=cat,
                total=float(cat_tot),
                count=category_counts[cat],
                percentage=pct,
            )
        )
    breakdown.sort(key=lambda x: x.total, reverse=True)

    # Monthly trend list sorted chronologically
    trend: List[MonthlySummary] = []
    for m_key in sorted(monthly_data.keys()):
        d = monthly_data[m_key]
        trend.append(
            MonthlySummary(
                month=d["month"],
                year=d["year"],
                total_income=float(d["income"]),
                total_expenses=float(d["expense"]),
                net_balance=float(d["income"] - d["expense"]),
                transaction_count=d["count"],
            )
        )

    return FinanceSummary(
        total_income=float(total_income),
        total_expenses=float(total_expenses),
        net_balance=float(net_balance),
        transaction_count=len(records),
        category_breakdown=breakdown,
        monthly_trend=trend,
    )

def generate_expenses_csv(
    db: Session,
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> str:
    """Generate a clean RFC 4180 CSV export of user transactions."""
    query = db.query(Expense)
    if user_id is not None:
        query = query.filter(Expense.user_id == user_id)
    else:
        query = query.filter(Expense.user_id.is_(None))
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)

    records = query.order_by(Expense.date.desc(), Expense.id.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["ID", "Date", "Title", "Category", "Type", "Amount", "Notes"])

    for r in records:
        writer.writerow([
            r.id,
            r.date.isoformat(),
            r.title,
            r.category,
            r.type,
            f"{r.amount:.2f}",
            r.notes or "",
        ])

    return output.getvalue()
