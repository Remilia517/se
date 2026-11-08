import os
import uuid
import requests

BASE_URL = os.getenv("STUDYTASK_BASE_URL", "http://localhost:8080")


def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/api/health", timeout=10)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"


def test_task_create_list_update_delete():
    unique_title = f"API integration test {uuid.uuid4().hex[:8]}"
    created_id = None

    try:
        create = requests.post(
            f"{BASE_URL}/api/tasks",
            json={"title": unique_title, "course": "測試課程"},
            timeout=10,
        )
        assert create.status_code == 201
        created = create.json()
        created_id = created["id"]
        assert created["title"] == unique_title
        assert created["status"] == "pending"

        listing = requests.get(f"{BASE_URL}/api/tasks", timeout=10)
        assert listing.status_code == 200
        assert any(task["id"] == created_id for task in listing.json())

        update = requests.patch(
            f"{BASE_URL}/api/tasks/{created_id}",
            json={"status": "done"},
            timeout=10,
        )
        assert update.status_code == 200
        assert update.json()["status"] == "done"
    finally:
        if created_id is not None:
            requests.delete(f"{BASE_URL}/api/tasks/{created_id}", timeout=10)


def test_create_task_without_title_returns_400():
    response = requests.post(
        f"{BASE_URL}/api/tasks", json={"title": "   "}, timeout=10
    )
    assert response.status_code == 400
