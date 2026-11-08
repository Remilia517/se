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
        self.assertIn("各課程完成進度".encode(), response.data)

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

    def test_calendar_page(self):
        response = self.client.get("/calendar?month=2026-11")
        self.assertEqual(response.status_code, 200)
        self.assertIn("2026 年 11 月".encode(), response.data)

    def test_csv_export(self):
        response = self.client.get("/export.csv")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.content_type)
        self.assertIn("事項名稱".encode("utf-8"), response.data)

    def test_priority_filter(self):
        response = self.client.get("/tasks?priority=高")
        self.assertEqual(response.status_code, 200)
        self.assertIn("人工智慧實務作業".encode(), response.data)


if __name__ == "__main__":
    unittest.main()
