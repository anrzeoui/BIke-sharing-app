"""US-01 browser-form flow, including CSRF protection."""

import tempfile
import unittest
from pathlib import Path

from bike_sharing import create_app
from bike_sharing.db import get_db


class RegistrationWebTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.app = create_app(
            {"TESTING": True, "SECRET_KEY": "test-only", "DATABASE": str(Path(directory.name) / "test.db")}
        )
        self.client = self.app.test_client()

    def form(self, **updates):
        self.client.get("/register")
        with self.client.session_transaction() as session:
            token = session["csrf_token"]
        data = {"full_name": "Ө. Анар", "email": "anar@example.com", "password": "BikePass123!", "csrf_token": token}
        data.update(updates)
        return data

    def test_registration_form_is_accessible(self):
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="csrf_token"', response.text)
        self.assertIn("Бүртгүүлэх", response.text)

    def test_successful_registration_redirects_with_confirmation(self):
        response = self.client.post("/register", data=self.form(), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Бүртгэл амжилттай үүслээ", response.text)
        with self.app.app_context():
            self.assertEqual(get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0], 1)

    def test_invalid_form_preserves_non_secret_fields_only(self):
        response = self.client.post("/register", data=self.form(password="short"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("anar@example.com", response.text)
        self.assertNotIn('value="short"', response.text)

    def test_duplicate_form_returns_conflict(self):
        self.client.post("/register", data=self.form())
        response = self.client.post("/register", data=self.form())
        self.assertEqual(response.status_code, 409)

    def test_missing_or_invalid_csrf_cannot_create_account(self):
        for token in [None, "wrong"]:
            data = self.form(csrf_token=token)
            if token is None:
                del data["csrf_token"]
            with self.subTest(token=token):
                self.assertEqual(self.client.post("/register", data=data).status_code, 400)
        with self.app.app_context():
            self.assertEqual(get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0], 0)

    def test_user_input_is_html_escaped(self):
        response = self.client.post(
            "/register", data=self.form(full_name='<script>alert("x")</script>', password="short")
        )
        self.assertNotIn('<script>alert("x")</script>', response.text)
        self.assertIn("&lt;script&gt;", response.text)


if __name__ == "__main__":
    unittest.main()
