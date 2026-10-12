from datetime import date

def test_budget_creation_and_thresholds(client, user_a):
    headers = user_a["headers"]
    today = date.today()

    # 1. Create a budget limit of 1000 for Food
    budget_res = client.post("/api/v1/budgets", json={
        "category": "Food",
        "monthly_limit": 1000.0,
        "month": today.month,
        "year": today.year
    }, headers=headers)
    assert budget_res.status_code == 201
    b_data = budget_res.json()
    assert b_data["monthly_limit"] == 1000.0
    assert b_data["spent"] == 0.0
    assert b_data["status"] == "normal"
    budget_id = b_data["id"]

    # 2. Add an expense of 850 in Food (85% utilization -> warning status)
    client.post("/api/v1/expenses", json={
        "title": "Supermarket Grocery",
        "amount": 850.0,
        "category": "Food",
        "type": "expense",
        "date": today.isoformat()
    }, headers=headers)

    # 3. Fetch budgets and verify utilization calculations
    list_res = client.get(f"/api/v1/budgets?month={today.month}&year={today.year}", headers=headers)
    assert list_res.status_code == 200
    budgets = list_res.json()
    assert len(budgets) == 1
    assert budgets[0]["spent"] == 850.0
    assert budgets[0]["remaining"] == 150.0
    assert budgets[0]["percentage"] == 85.0
    assert budgets[0]["status"] == "warning"

    # 4. Add another expense of 200 in Food (105% utilization -> exceeded status)
    client.post("/api/v1/expenses", json={
        "title": "Bakery",
        "amount": 200.0,
        "category": "Food",
        "type": "expense",
        "date": today.isoformat()
    }, headers=headers)

    list_res2 = client.get(f"/api/v1/budgets?month={today.month}&year={today.year}", headers=headers)
    assert list_res2.json()[0]["spent"] == 1050.0
    assert list_res2.json()[0]["status"] == "exceeded"

    # 5. Delete budget
    del_res = client.delete(f"/api/v1/budgets/{budget_id}", headers=headers)
    assert del_res.status_code == 200
