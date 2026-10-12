import abc
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List, Optional
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.core.config import settings
from app.models.expense import Expense
from app.models.budget import Budget
from app.services.budget_service import get_budgets
from app.schemas.ai import AIChatRequest, AIChatResponse

class BaseAIProvider(abc.ABC):
    """Abstract base class for all SpendSense AI providers."""

    @abc.abstractmethod
    async def generate_response(
        self,
        user_message: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]]
    ) -> str:
        pass

class MockAIProvider(BaseAIProvider):
    """Deterministic local AI provider for development, testing, and offline use."""

    async def generate_response(
        self,
        user_message: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]]
    ) -> str:
        msg = user_message.lower().strip()
        month_name = context.get("month_name", "this month")
        income = context.get("total_income", 0.0)
        expenses = context.get("total_expenses", 0.0)
        balance = context.get("current_balance", 0.0)
        categories = context.get("category_breakdown", {})
        budgets = context.get("budgets", [])

        # Sort categories by spending descending
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        top_cat = sorted_cats[0] if sorted_cats else None

        if any(w in msg for w in ["spend", "spent", "how much", "cost"]):
            if "category" in msg or "most" in msg:
                if top_cat:
                    return (
                        f"📊 **Category Breakdown Fact:** Your highest expense category in {month_name} "
                        f"is **{top_cat[0]}** at **₹{top_cat[1]:.2f}** "
                        f"({(top_cat[1]/expenses*100):.1f}% of your total spending).\n\n"
                        f"💡 *Suggestion:* Look into smaller daily purchases in {top_cat[0]} to reduce leakage."
                    )
                return f"You don't have any logged expenses in {month_name} yet."
            return (
                f"📊 **Verified Financial Fact:** You have spent a total of **₹{expenses:.2f}** in {month_name}.\n"
                f"Total income logged: **₹{income:.2f}**.\n"
                f"Current net balance: **₹{balance:.2f}**."
            )

        if any(w in msg for w in ["income", "earn", "salary"]):
            return (
                f"💰 **Verified Financial Fact:** Your total income recorded for {month_name} is **₹{income:.2f}**."
            )

        if any(w in msg for w in ["balance", "left", "net", "remaining"]):
            status_text = "healthy" if balance >= 0 else "in deficit"
            return (
                f"⚖️ **Verified Financial Fact:** Your current net balance is **₹{balance:.2f}** ({status_text}).\n"
                f"Total Income: ₹{income:.2f} | Total Expenses: ₹{expenses:.2f}."
            )

        if any(w in msg for w in ["budget", "limit", "exceed"]):
            if not budgets:
                return (
                    f"⚠️ You haven't set any monthly budgets for {month_name} yet. "
                    f"Setting category budgets helps keep your spending on track!"
                )
            
            exceeded = [b for b in budgets if b["status"] == "exceeded"]
            warning = [b for b in budgets if b["status"] == "warning"]
            lines = [f"📋 **Budget Status for {month_name}:**"]
            for b in budgets:
                flag = "🔴 EXCEEDED" if b["status"] == "exceeded" else ("🟡 WARNING" if b["status"] == "warning" else "🟢 OK")
                lines.append(f"- **{b['category']}**: Spent ₹{b['spent']:.2f} of ₹{b['limit']:.2f} ({b['percentage']}%) — {flag}")
            
            if exceeded:
                lines.append("\n🚨 *Attention:* You have exceeded your budget limits in: " + ", ".join(b['category'] for b in exceeded))
            elif warning:
                lines.append("\n⚠️ *Notice:* You are approaching budget limits in: " + ", ".join(b['category'] for b in warning))
            else:
                lines.append("\n✅ Great job! All your tracked categories are currently within budget.")
            return "\n".join(lines)

        if any(w in msg for w in ["reduce", "save", "cut", "habit", "advice", "suggest"]):
            advice = [f"💡 **AI Spending Insights & Recommendations:**"]
            if top_cat:
                advice.append(f"1. **Target Top Category:** Your highest spending is in **{top_cat[0]}** (₹{top_cat[1]:.2f}). Setting a strict weekly cap could save you up to 15-20%.")
            if balance < 0:
                advice.append("2. **Deficit Alert:** Your expenses exceed your income this month. Prioritize non-discretionary necessities only.")
            else:
                advice.append(f"2. **Savings Cushion:** You currently have ₹{balance:.2f} in positive cash flow. Consider allocating 20% to savings or emergency funds.")
            advice.append("3. **Recurring Audits:** Review recurring subscriptions and small daily transaction patterns.")
            return "\n".join(advice)

        # Default summary response
        res = [
            f"👋 Hello! Here is your quick financial summary for **{month_name}**:",
            f"- **Net Balance:** ₹{balance:.2f}",
            f"- **Total Income:** ₹{income:.2f}",
            f"- **Total Expenses:** ₹{expenses:.2f}",
        ]
        if top_cat:
            res.append(f"- **Top Spending Category:** {top_cat[0]} (₹{top_cat[1]:.2f})")
        res.append("\nYou can ask me specific questions like 'How much did I spend?', 'Am I exceeding my budget?', or 'Where could I reduce spending?'.")
        return "\n".join(res)

class GeminiProvider(BaseAIProvider):
    """Google Gemini LLM provider integration."""

    async def generate_response(
        self,
        user_message: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]]
    ) -> str:
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.strip() == "":
            raise ValueError("GEMINI_API_KEY is not configured in backend environment.")

        system_instruction = (
            "You are SpendSense AI, an expert and empathetic personal finance assistant.\n"
            "Here is the user's verified, trusted database context (DO NOT hallucinate other numbers):\n"
            f"Month: {context.get('month_name')}\n"
            f"Total Income: ₹{context.get('total_income', 0.0):.2f}\n"
            f"Total Expenses: ₹{context.get('total_expenses', 0.0):.2f}\n"
            f"Net Balance: ₹{context.get('current_balance', 0.0):.2f}\n"
            f"Category Breakdown: {context.get('category_breakdown', {})}\n"
            f"Budgets: {context.get('budgets', [])}\n"
            f"Recent Transactions: {context.get('recent_transactions', [])}\n\n"
            "Rules:\n"
            "1. Ground all financial statements in the verified figures above.\n"
            "2. Never claim you can perform transfers, write code, or execute database operations.\n"
            "3. Clearly distinguish calculated facts from subjective advice.\n"
            "4. Keep responses concise, actionable, and formatted in markdown."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        
        contents = [{"role": "user", "parts": [{"text": system_instruction}]}]
        for h in history[-4:]:
            role = "user" if h["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h["content"]}]})
        contents.append({"role": "user", "parts": [{"text": user_message}]})

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json={"contents": contents})
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API returned status {resp.status_code}: {resp.text}")
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "No response generated.")
            return "Unable to parse response from Gemini."

class OpenAIProvider(BaseAIProvider):
    """OpenAI / compatible LLM provider integration."""

    async def generate_response(
        self,
        user_message: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]]
    ) -> str:
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.strip() == "":
            raise ValueError("OPENAI_API_KEY is not configured in backend environment.")

        system_prompt = (
            "You are SpendSense AI, a personal financial assistant.\n"
            f"Verified Financial Context for {context.get('month_name')}:\n"
            f"- Total Income: ₹{context.get('total_income', 0.0):.2f}\n"
            f"- Total Expenses: ₹{context.get('total_expenses', 0.0):.2f}\n"
            f"- Net Balance: ₹{context.get('current_balance', 0.0):.2f}\n"
            f"- Category Breakdown: {context.get('category_breakdown', {})}\n"
            f"- Budgets: {context.get('budgets', [])}\n\n"
            "Ground your replies strictly on these figures. Do not fabricate numbers."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-4:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_message})

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                json={"model": "gpt-4o-mini", "messages": messages, "temperature": 0.3}
            )
            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI API returned status {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

class GroqProvider(BaseAIProvider):
    """Groq Cloud LLM provider integration using OpenAI-compatible endpoint."""

    async def generate_response(
        self,
        user_message: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]]
    ) -> str:
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY.strip() == "":
            raise ValueError("GROQ_API_KEY is not configured in backend environment.")

        system_prompt = (
            "You are SpendSense AI, a personal financial assistant.\n"
            f"Verified Financial Context for {context.get('month_name')}:\n"
            f"- Total Income: ₹{context.get('total_income', 0.0):.2f}\n"
            f"- Total Expenses: ₹{context.get('total_expenses', 0.0):.2f}\n"
            f"- Net Balance: ₹{context.get('current_balance', 0.0):.2f}\n"
            f"- Category Breakdown: {context.get('category_breakdown', {})}\n"
            f"- Budgets: {context.get('budgets', [])}\n\n"
            "Ground your replies strictly on these figures. Do not fabricate numbers."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-4:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_message})

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.3}
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Groq API returned status {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

def get_user_financial_context(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
    """Extract verified financial facts from the database for the current user and month."""
    today = date.today()
    current_month = today.month
    current_year = today.year
    month_name = today.strftime("%B %Y")

    query = db.query(Expense).filter(
        extract("month", Expense.date) == current_month,
        extract("year", Expense.date) == current_year
    )
    if user_id is not None:
        query = query.filter(Expense.user_id == user_id)
    else:
        query = query.filter(Expense.user_id.is_(None))

    monthly_records = query.all()
    total_income = Decimal("0.00")
    total_expenses = Decimal("0.00")
    category_breakdown: Dict[str, float] = {}

    for r in monthly_records:
        amt = Decimal(str(round(r.amount, 2)))
        if r.type == "income":
            total_income += amt
        elif r.type == "expense":
            total_expenses += amt
            cat = r.category.strip()
            category_breakdown[cat] = round(category_breakdown.get(cat, 0.0) + float(amt), 2)

    budgets_data = get_budgets(db, user_id=user_id, month=current_month, year=current_year)
    formatted_budgets = [
        {
            "category": b.category,
            "limit": b.monthly_limit,
            "spent": b.spent,
            "remaining": b.remaining,
            "percentage": b.percentage,
            "status": b.status
        }
        for b in budgets_data
    ]

    recent_query = db.query(Expense)
    if user_id is not None:
        recent_query = recent_query.filter(Expense.user_id == user_id)
    else:
        recent_query = recent_query.filter(Expense.user_id.is_(None))
    recent = recent_query.order_by(Expense.date.desc(), Expense.id.desc()).limit(5).all()
    formatted_recent = [
        {"title": r.title, "amount": r.amount, "type": r.type, "category": r.category, "date": r.date.isoformat()}
        for r in recent
    ]

    return {
        "month_name": month_name,
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "current_balance": float(total_income - total_expenses),
        "category_breakdown": category_breakdown,
        "budgets": formatted_budgets,
        "recent_transactions": formatted_recent,
    }

async def process_ai_chat(
    db: Session,
    request: AIChatRequest,
    user_id: Optional[int] = None
) -> AIChatResponse:
    """Orchestrate AI interaction using the configured provider and grounded facts."""
    context = get_user_financial_context(db, user_id=user_id)
    history_dicts = [{"role": m.role, "content": m.content} for m in (request.history or [])]
    
    provider_name = settings.AI_PROVIDER.lower().strip()
    
    # Provider selection
    provider: BaseAIProvider
    if provider_name == "gemini":
        provider = GeminiProvider()
    elif provider_name == "groq":
        provider = GroqProvider()
    elif provider_name == "openai":
        provider = OpenAIProvider()
    else:
        provider = MockAIProvider()

    try:
        reply = await provider.generate_response(request.message, context, history_dicts)
        return AIChatResponse(
            reply=reply,
            context_summary=f"Context: {context['month_name']} (Spent: ₹{context['total_expenses']:.2f}, Balance: ₹{context['current_balance']:.2f})",
            provider=provider_name,
            status="success"
        )
    except ValueError as val_err:
        # Missing API Key scenario
        mock_fallback = MockAIProvider()
        fallback_reply = await mock_fallback.generate_response(request.message, context, history_dicts)
        notice = f"\n\n*(Note: Live {provider_name.title()} key not detected. Provided response using local financial reasoning engine. Configure `{provider_name.upper()}_API_KEY` in .env for full LLM integration).* "
        return AIChatResponse(
            reply=fallback_reply + notice,
            context_summary=f"Context: {context['month_name']} (Spent: ₹{context['total_expenses']:.2f})",
            provider=f"{provider_name}-fallback",
            status="fallback"
        )
    except Exception as e:
        # Fallback gracefully
        mock_fallback = MockAIProvider()
        fallback_reply = await mock_fallback.generate_response(request.message, context, history_dicts)
        return AIChatResponse(
            reply=f"{fallback_reply}\n\n*(Provider warning: {str(e)[:100]}. Fallback calculation returned).* ",
            context_summary=None,
            provider="local-engine",
            status="fallback"
        )
