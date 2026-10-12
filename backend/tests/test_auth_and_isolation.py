def test_user_registration_and_login(client):
    # 1. Register new user
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "strongpassword123",
        "full_name": "New User"
    })
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["email"] == "newuser@example.com"
    assert "password" not in user_data

    # 2. Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": "newuser@example.com",
        "password": "strongpassword123"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Read profile with token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "newuser@example.com"

def test_login_invalid_password(client, user_a):
    res = client.post("/api/v1/auth/login", json={
        "email": "test_user_a@example.com",
        "password": "incorrect_password"
    })
    assert res.status_code == 401

def test_multi_tenant_data_isolation(client, user_a, user_b):
    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    # User A creates a transaction
    res_a = client.post("/api/v1/expenses", json={
        "title": "Alice Private Expense",
        "amount": 120.0,
        "category": "Shopping",
        "type": "expense"
    }, headers=headers_a)
    assert res_a.status_code == 201
    exp_a_id = res_a.json()["id"]

    # User B creates a transaction
    res_b = client.post("/api/v1/expenses", json={
        "title": "Bob Private Salary",
        "amount": 8000.0,
        "category": "Salary",
        "type": "income"
    }, headers=headers_b)
    assert res_b.status_code == 201
    exp_b_id = res_b.json()["id"]

    # User A views their transactions
    user_a_list = client.get("/api/v1/expenses", headers=headers_a).json()
    assert any(x["id"] == exp_a_id for x in user_a_list)
    assert not any(x["id"] == exp_b_id for x in user_a_list)

    # User B views their transactions
    user_b_list = client.get("/api/v1/expenses", headers=headers_b).json()
    assert any(x["id"] == exp_b_id for x in user_b_list)
    assert not any(x["id"] == exp_a_id for x in user_b_list)

    # User B attempts to access or modify User A's transaction -> MUST return 404
    get_forbidden = client.get(f"/api/v1/expenses/{exp_a_id}", headers=headers_b)
    assert get_forbidden.status_code == 404

    put_forbidden = client.put(f"/api/v1/expenses/{exp_a_id}", json={"amount": 999.0}, headers=headers_b)
    assert put_forbidden.status_code == 404

    del_forbidden = client.delete(f"/api/v1/expenses/{exp_a_id}", headers=headers_b)
    assert del_forbidden.status_code == 404

    # Anonymous user (no auth header) MUST NOT see Alice's or Bob's transactions
    anon_list = client.get("/api/v1/expenses").json()
    assert not any(x["id"] in [exp_a_id, exp_b_id] for x in anon_list)

    # Anonymous user cannot fetch Alice's transaction by ID
    assert client.get(f"/api/v1/expenses/{exp_a_id}").status_code == 404

def test_health_and_root_endpoints(client):
    # Health check endpoint
    health_res = client.get("/health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["status"] == "ok"
    assert "version" in health_data

    # Root welcome/info endpoint
    root_res = client.get("/")
    assert root_res.status_code == 200
    root_data = root_res.json()
    assert root_data["status"] == "healthy"
    assert "app_name" in root_data
