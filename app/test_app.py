from app import app


def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_create_task_requires_title():
    client = app.test_client()
    resp = client.post("/api/tasks", json={"title": "   "})
    assert resp.status_code == 400
