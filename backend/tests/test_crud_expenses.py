def test_create_and_get_expense(client, user_a):
    headers = user_a["headers"]
    
    # 1. Create Expense
    payload = {
        "title": "Groceries at Market",
        "amount": 450.75,
        "category": "Food",
        "type": "expense",
        "notes": "Weekly fruits & vegetables"
    }
    create_res = client.post("/api/v1/expenses", json=payload, headers=headers)
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["title"] == "Groceries at Market"
    assert data["amount"] == 450.75
    assert data["category"] == "Food"
    assert data["type"] == "expense"
    exp_id = data["id"]

    # 2. Get Expense by ID
    get_res = client.get(f"/api/v1/expenses/{exp_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Groceries at Market"

    # 3. Update Expense
    update_res = client.put(f"/api/v1/expenses/{exp_id}", json={"amount": 500.00}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["amount"] == 500.00

    # 4. Delete Expense
    del_res = client.delete(f"/api/v1/expenses/{exp_id}", headers=headers)
    assert del_res.status_code == 200

    # 5. Verify 404 after deletion
    not_found = client.get(f"/api/v1/expenses/{exp_id}", headers=headers)
    assert not_found.status_code == 404

def test_expense_validation(client, user_a):
    headers = user_a["headers"]

    # Test negative amount
    res = client.post("/api/v1/expenses", json={
        "title": "Invalid", "amount": -10.0, "category": "Food", "type": "expense"
    }, headers=headers)
    assert res.status_code == 422

    # Test zero amount
    res = client.post("/api/v1/expenses", json={
        "title": "Invalid", "amount": 0.0, "category": "Food", "type": "expense"
    }, headers=headers)
    assert res.status_code == 422

    # Test whitespace-only title
    res = client.post("/api/v1/expenses", json={
        "title": "   ", "amount": 100.0, "category": "Food", "type": "expense"
    }, headers=headers)
    assert res.status_code == 422

    # Test invalid type
    res = client.post("/api/v1/expenses", json={
        "title": "Invalid", "amount": 100.0, "category": "Food", "type": "investment_unsupported"
    }, headers=headers)
    assert res.status_code == 422

def test_nonexistent_expense_404(client, user_a):
    headers = user_a["headers"]
    assert client.get("/api/v1/expenses/99999", headers=headers).status_code == 404
    assert client.put("/api/v1/expenses/99999", json={"title": "N/A"}, headers=headers).status_code == 404
    assert client.delete("/api/v1/expenses/99999", headers=headers).status_code == 404
