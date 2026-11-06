import tempfile
import unittest
from pathlib import Path

import app as study


class StudyFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        study.DB_PATH = Path(self.temp.name) / "test.db"
        study.init_db()
        study.app.config.update(TESTING=True)
        self.client = study.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def test_dashboard_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("StudyFlow".encode(), response.data)

    def test_create_task(self):
        response = self.client.post("/tasks/new", data={
            "title": "測試作業", "course": "軟體工程",
            "description": "測試內容", "due_date": "2026-12-01",
            "priority": "高"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("測試作業".encode(), response.data)

    def test_reject_missing_title(self):
        response = self.client.post("/tasks/new", data={
            "title": "", "due_date": "2026-12-01"
        }, follow_redirects=True)
        self.assertIn("必填欄位".encode(), response.data)

    def test_search_task(self):
        response = self.client.get("/tasks?q=資料庫")
        self.assertIn("資料庫正規化報告".encode(), response.data)

    def test_toggle_complete(self):
        with study.connect() as db:
            task_id = db.execute("SELECT id FROM tasks LIMIT 1").fetchone()["id"]
        response = self.client.post(f"/tasks/{task_id}/toggle", follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
