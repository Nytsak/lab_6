import uuid


def test_user_signup_ok(client):
    res = client.post(
        "/api/auth/register",
        json={"username": "student99", "password": "strong_pass!"},
    )
    assert res.status_code == 201
    json_data = res.json()
    assert "password" not in json_data
    assert "hashed_password" not in json_data
    assert json_data["username"] == "student99"
    assert "id" in json_data


def test_signup_existing_user_fails(client):
    user_data = {"username": "test_student_1", "password": "strong_pass!"}
    client.post("/api/auth/register", json=user_data)
    
    res = client.post("/api/auth/register", json=user_data)
    assert res.status_code == 409
    assert "already taken" in res.json()["detail"]


def test_signup_weak_password_rejected(client):
    res = client.post(
        "/api/auth/register",
        json={"username": "user1", "password": "12"},
    )
    assert res.status_code == 422


def test_user_authentication_success(client):
    client.post(
        "/api/auth/register",
        json={"username": "test_login_user", "password": "my_secret_123"},
    )
    res = client.post(
        "/api/auth/login",
        data={"username": "test_login_user", "password": "my_secret_123"},
    )
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["token_type"] == "bearer"
    assert "access_token" in json_data
    assert "refresh_token" in json_data


def test_auth_with_bad_password(client):
    client.post(
        "/api/auth/register",
        json={"username": "test_user_pwd", "password": "my_secret_123"},
    )
    res = client.post(
        "/api/auth/login",
        data={"username": "test_user_pwd", "password": "wrong_password_here"},
    )
    assert res.status_code == 401


def test_auth_unknown_user_fails(client):
    res = client.post(
        "/api/auth/login",
        data={"username": "nobody_here", "password": "password123"},
    )
    assert res.status_code == 401


def test_refreshing_token_works(client):
    client.post(
        "/api/auth/register",
        json={"username": "ref_user", "password": "password123"},
    )
    login_req = client.post(
        "/api/auth/login",
        data={"username": "ref_user", "password": "password123"},
    )
    tokens = login_req.json()
    old_acc = tokens["access_token"]
    old_ref = tokens["refresh_token"]

    refresh_req = client.post("/api/auth/refresh", json={"refresh_token": old_ref})
    
    assert refresh_req.status_code == 200
    new_tokens = refresh_req.json()
    
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["access_token"] != old_acc
    assert new_tokens["refresh_token"] != old_ref


def test_old_refresh_token_is_invalidated_after_use(client):
    client.post(
        "/api/auth/register",
        json={"username": "rot_user", "password": "password123"},
    )
    login_req = client.post(
        "/api/auth/login",
        data={"username": "rot_user", "password": "password123"},
    )
    old_ref = login_req.json()["refresh_token"]

    client.post("/api/auth/refresh", json={"refresh_token": old_ref})

    second_req = client.post("/api/auth/refresh", json={"refresh_token": old_ref})
    assert second_req.status_code == 401


def test_refresh_fails_with_fake_token(client):
    res = client.post(
        "/api/auth/refresh", json={"refresh_token": "fake.token.value"}
    )
    assert res.status_code == 401


def test_user_logout_clears_refresh_token(client):
    client.post(
        "/api/auth/register",
        json={"username": "log_out_guy", "password": "password123"},
    )
    login_req = client.post(
        "/api/auth/login",
        data={"username": "log_out_guy", "password": "password123"},
    )
    ref_token = login_req.json()["refresh_token"]

    logout_req = client.post("/api/auth/logout", json={"refresh_token": ref_token})
    assert logout_req.status_code == 204

    refresh_req = client.post("/api/auth/refresh", json={"refresh_token": ref_token})
    assert refresh_req.status_code == 401


def test_fetch_all_books(client, auth_headers):
    res = client.get("/api/books", headers=auth_headers)
    assert res.status_code == 200
    resp_data = res.json()
    
    assert "items" in resp_data
    assert len(resp_data["items"]) >= 1
    assert resp_data["items"][0]["title"] == "Alice`s Adventures in Wonderland"


def test_fetch_single_book_by_id(client, auth_headers):
    all_books = client.get("/api/books", headers=auth_headers).json()
    target_id = all_books["items"][0]["id"]

    res = client.get(f"/api/books/{target_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Alice`s Adventures in Wonderland"


def test_fetch_missing_book_returns_404(client, auth_headers):
    fake_id = str(uuid.uuid4())
    res = client.get(f"/api/books/{fake_id}", headers=auth_headers)
    
    assert res.status_code == 404
    assert res.json()["detail"] == "Book not found"


def test_add_new_book(client, auth_headers):
    book_payload = {
        "title": "The Lord of the Rings",
        "author": "J. R. R. Tolkien",
        "description": "Frodo's journey",
        "status": "available",
        "release_year": 1954,
    }
    res = client.post("/api/books", json=book_payload, headers=auth_headers)
    
    assert res.status_code == 201
    resp_data = res.json()
    assert "id" in resp_data
    assert resp_data["title"] == book_payload["title"]


def test_add_book_with_bad_data_fails(client, auth_headers):
    bad_book = {
        "title": "Bad Book Year",
        "author": "Unknown",
        "release_year": -15,
    }
    res = client.post("/api/books", json=bad_book, headers=auth_headers)
    assert res.status_code == 422


def test_remove_book_by_id(client, auth_headers):
    books = client.get("/api/books", headers=auth_headers).json()
    target_id = books["items"][0]["id"]

    res_delete = client.delete(f"/api/books/{target_id}", headers=auth_headers)
    assert res_delete.status_code == 204

    res_get = client.get(f"/api/books/{target_id}", headers=auth_headers)
    assert res_get.status_code == 404


def test_books_list_pagination(client, auth_headers):
    res = client.get("/api/books?limit=2&offset=0", headers=auth_headers)
    assert res.status_code == 200
    resp_data = res.json()

    assert "items" in resp_data
    assert "total" in resp_data
    assert isinstance(resp_data["items"], list)
    assert resp_data["limit"] == 2
    assert resp_data["offset"] == 0


def test_books_endpoints_are_protected(client):
    get_res = client.get("/api/books")
    assert get_res.status_code == 401
    
    post_res = client.post("/api/books", json={})
    assert post_res.status_code == 401
