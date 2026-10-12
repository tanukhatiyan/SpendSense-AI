from datetime import date

def test_smart_category_inference_on_create(client, user_a):
    headers = user_a["headers"]
    today = date.today()

    # 1. Title "uber" with default category "Food" should auto-infer "Transport"
    res1 = client.post("/api/v1/expenses", json={
        "title": "uber",
        "amount": 500.0,
        "category": "Food",
        "type": "expense",
        "date": today.isoformat()
    }, headers=headers)
    assert res1.status_code == 201
    assert res1.json()["category"] == "Transport"

    # 2. Title "swiggy dinner" with "Other" should auto-infer "Food"
    res2 = client.post("/api/v1/expenses", json={
        "title": "swiggy dinner",
        "amount": 350.0,
        "category": "Other",
        "type": "expense",
        "date": today.isoformat()
    }, headers=headers)
    assert res2.status_code == 201
    assert res2.json()["category"] == "Food"

    # 3. Explicit non-default category should be preserved
    res3 = client.post("/api/v1/expenses", json={
        "title": "uber trip to cinema",
        "amount": 400.0,
        "category": "Entertainment",
        "type": "expense",
        "date": today.isoformat()
    }, headers=headers)
    assert res3.status_code == 201
    assert res3.json()["category"] == "Entertainment"

def test_ai_query_merchant_and_category_accuracy(client, user_a):
    headers = user_a["headers"]
    today = date.today()

    # Create two 500 INR expenses
    client.post("/api/v1/expenses", json={
        "title": "uber",
        "amount": 500.0,
        "category": "Transport",
        "type": "expense",
        "date": today.isoformat()
    }, headers=headers)

    client.post("/api/v1/expenses", json={
        "title": "grocery",
        "amount": 500.0,
        "category": "Food",
        "type": "expense",
        "date": today.isoformat()
    }, headers=headers)

    # 1. Ask specifically about "uber"
    ai_uber = client.post("/api/v1/ai/chat", json={
        "message": "How much did I spend on uber?"
    }, headers=headers)
    assert ai_uber.status_code == 200
    uber_reply = ai_uber.json()["reply"]
    assert "500.00" in uber_reply or "500" in uber_reply
    assert "1000.00" not in uber_reply  # Must not return total spending for specific merchant

    # 2. Ask specifically about "food"
    ai_food = client.post("/api/v1/ai/chat", json={
        "message": "How much did I spend on food?"
    }, headers=headers)
    assert ai_food.status_code == 200
    food_reply = ai_food.json()["reply"]
    assert "500.00" in food_reply or "500" in food_reply
    assert "1000.00" not in food_reply  # Must not return total spending for specific category

    # 3. Ask specifically about "transport"
    ai_trans = client.post("/api/v1/ai/chat", json={
        "message": "How much did I spend on transport?"
    }, headers=headers)
    assert ai_trans.status_code == 200
    trans_reply = ai_trans.json()["reply"]
    assert "500.00" in trans_reply or "500" in trans_reply
    assert "1000.00" not in trans_reply

    # 4. Ask general total spending inquiry
    ai_total = client.post("/api/v1/ai/chat", json={
        "message": "How much did I spend this month?"
    }, headers=headers)
    assert ai_total.status_code == 200
    total_reply = ai_total.json()["reply"]
    assert "1000.00" in total_reply or "1000" in total_reply
