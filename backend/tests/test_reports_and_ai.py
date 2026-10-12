from datetime import date

def test_reports_and_csv_export(client, user_a):
    headers = user_a["headers"]
    today = date.today()

    # Add income & expenses
    client.post("/api/v1/expenses", json={
        "title": "Client Retainer", "amount": 25000.0, "category": "Salary", "type": "income", "date": today.isoformat()
    }, headers=headers)

    client.post("/api/v1/expenses", json={
        "title": "Electricity Bill", "amount": 2500.0, "category": "Utilities", "type": "expense", "date": today.isoformat()
    }, headers=headers)

    # 1. Summary Report
    summary_res = client.get("/api/v1/reports/summary", headers=headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_income"] == 25000.0
    assert summary["total_expenses"] == 2500.0
    assert summary["net_balance"] == 22500.0
    assert len(summary["category_breakdown"]) == 1
    assert summary["category_breakdown"][0]["category"] == "Utilities"

    # 2. CSV Export
    csv_res = client.get("/api/v1/reports/export-csv", headers=headers)
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert "Client Retainer" in csv_res.text
    assert "Electricity Bill" in csv_res.text

def test_ai_assistant_grounding(client, user_a):
    headers = user_a["headers"]
    today = date.today()

    # Add transaction
    client.post("/api/v1/expenses", json={
        "title": "Laptop Sleeve", "amount": 950.0, "category": "Shopping", "type": "expense", "date": today.isoformat()
    }, headers=headers)

    # Ask spending inquiry
    ai_res = client.post("/api/v1/ai/chat", json={
        "message": "How much did I spend this month?"
    }, headers=headers)
    assert ai_res.status_code == 200
    ai_data = ai_res.json()
    assert "950.00" in ai_data["reply"] or "950" in ai_data["reply"]
    assert ai_data["status"] in ["success", "fallback"]

    # Ask budget inquiry
    ai_budget_res = client.post("/api/v1/ai/chat", json={
        "message": "Am I exceeding my budget?"
    }, headers=headers)
    assert ai_budget_res.status_code == 200
