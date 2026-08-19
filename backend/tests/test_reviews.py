

def test_create_review_from_snippet(client, auth_headers):
    payload = {
        "filename": "test_buggy.py",
        "source_code": """
def buggy_func(x=[]):
    try:
        x.append(1)
        return eval("1+1")
    except:
        pass
""",
        "source_type": "snippet"
    }
    response = client.post("/api/reviews", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["filename"] == "test_buggy.py"
    assert data["overall_score"] < 100.0
    assert len(data["findings"]) > 0
    assert "fixed_code" in data
    assert data["ai_available"] is True


def test_upload_py_file(client, auth_headers):
    file_content = b"""
def sample(a, b):
    return a + b
"""
    response = client.post(
        "/api/reviews/upload",
        files={"file": ("sample.py", file_content, "text/x-python")},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "sample.py"
    assert data["overall_score"] >= 90.0


def test_upload_non_py_rejected(client, auth_headers):
    file_content = b"echo 'hello'"
    response = client.post(
        "/api/reviews/upload",
        files={"file": ("script.sh", file_content, "application/x-sh")},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_get_review_history_and_detail_and_delete(client, auth_headers):
    # 1. Create review
    payload = {
        "filename": "history_test.py",
        "source_code": "def func(): return 1\n",
        "source_type": "snippet"
    }
    create_res = client.post("/api/reviews", json=payload, headers=auth_headers)
    review_id = create_res.json()["id"]

    # 2. Get list
    list_res = client.get("/api/reviews", headers=auth_headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(r["id"] == review_id for r in items)

    # 3. Get single detail
    detail_res = client.get(f"/api/reviews/{review_id}", headers=auth_headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == review_id

    # 4. Get dashboard stats
    stats_res = client.get("/api/reviews/stats/dashboard", headers=auth_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_reviews"] >= 1

    # 5. Delete review
    del_res = client.delete(f"/api/reviews/{review_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # 6. Verify deleted
    get_after = client.get(f"/api/reviews/{review_id}", headers=auth_headers)
    assert get_after.status_code == 404
