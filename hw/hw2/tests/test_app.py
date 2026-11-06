import tempfile
import unittest
from pathlib import Path

import app as portal


class PortalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        portal.DATABASE = Path(self.tmp.name) / "test.db"
        portal.init_db()
        portal.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = portal.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def login(self):
        return self.client.post("/login", data={
            "student_id": "412630001", "password": "123456"
        }, follow_redirects=True)

    def test_login_and_dashboard(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn("首頁總覽".encode(), response.data)

    def test_reject_bad_login(self):
        response = self.client.post("/login", data={
            "student_id": "wrong", "password": "wrong"
        }, follow_redirects=True)
        self.assertIn("學號或密碼錯誤".encode(), response.data)

    def test_course_page_requires_login(self):
        response = self.client.get("/courses")
        self.assertEqual(response.status_code, 302)

    def test_course_search(self):
        self.login()
        response = self.client.get("/courses?q=人工智慧")
        self.assertIn("人工智慧實務".encode(), response.data)

    def test_enroll_course(self):
        self.login()
        # CS304 is Thursday; does not conflict with the initial three enrolled courses.
        response = self.client.post("/courses/CS304/add", follow_redirects=True)
        self.assertIn("成功加選".encode(), response.data)


if __name__ == "__main__":
    unittest.main()
