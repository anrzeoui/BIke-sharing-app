"""US-02 authentication, session and authorization regressions."""

import tempfile
import unittest
from pathlib import Path

from bike_sharing import create_app
from bike_sharing.auth import AuthService, ValidationError
from bike_sharing.db import get_db


class LoginTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.app = create_app(
            {"TESTING": True, "SECRET_KEY": "test-only", "DATABASE": str(Path(directory.name) / "test.db")}
        )
        self.client = self.app.test_client()
        with self.app.app_context():
            self.user = AuthService(get_db()).register("Ө. Анар", "anar@example.com", "BikePass123!")

    def token(self, client=None):
        client = client or self.client
        client.get("/login")
        with client.session_transaction() as session:
            return session["csrf_token"]

    def login(self, **updates):
        data = {"email": "anar@example.com", "password": "BikePass123!", "csrf_token": self.token()}
        data.update(updates)
        return self.client.post("/login", data=data)

    def test_service_authenticates_normalized_email(self):
        with self.app.app_context():
            user = AuthService(get_db()).login(" ANAR@Example.com ", "BikePass123!")
            self.assertEqual(user.id, self.user.id)
            self.assertNotIn("password_hash", vars(user))

    def test_service_returns_same_error_for_invalid_credentials(self):
        cases = [
            ("anar@example.com", "wrongpass"),
            ("missing@example.com", "BikePass123!"),
            ("' OR 1=1 --", "BikePass123!"),
            (None, "BikePass123!"),
            ("anar@example.com", None),
            ("anar@example.com", "x" * 129),
        ]
        messages = []
        with self.app.app_context():
            for email, password in cases:
                with self.subTest(email=email), self.assertRaises(ValidationError) as raised:
                    AuthService(get_db()).login(email, password)
                messages.append(str(raised.exception))
                self.assertEqual(raised.exception.status_code, 401)
        self.assertEqual(len(set(messages)), 1)

    def test_login_form_is_accessible(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn('autocomplete="current-password"', response.text)

    def test_successful_login_redirects_to_private_account(self):
        response = self.login()
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.location.endswith("/account"))
        account = self.client.get("/account")
        self.assertEqual(account.status_code, 200)
        self.assertIn("Ө. Анар", account.text)
        self.assertIn("anar@example.com", account.text)

    def test_failed_login_does_not_create_session(self):
        response = self.login(password="wrongpass")
        self.assertEqual(response.status_code, 401)
        with self.client.session_transaction() as session:
            self.assertNotIn("user_id", session)
        self.assertNotIn("BikePass123!", response.text)
        self.assertNotIn('value="wrongpass"', response.text)

    def test_account_requires_login(self):
        response = self.client.get("/account")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/login"))

    def test_login_replaces_old_session_and_csrf_token(self):
        old_token = self.token()
        with self.client.session_transaction() as session:
            session["unexpected"] = "old session data"
        self.client.post(
            "/login", data={"email": "anar@example.com", "password": "BikePass123!", "csrf_token": old_token}
        )
        self.client.get("/account")
        with self.client.session_transaction() as session:
            self.assertNotIn("unexpected", session)
            self.assertEqual(session["user_id"], self.user.id)
            self.assertNotEqual(session["csrf_token"], old_token)
            self.assertNotIn("password", session)
            self.assertNotIn("password_hash", session)

    def test_logout_clears_access_and_rejects_old_csrf(self):
        self.login()
        self.client.get("/account")
        with self.client.session_transaction() as session:
            token = session["csrf_token"]
        response = self.client.post("/logout", data={"csrf_token": token})
        self.assertEqual(response.status_code, 303)
        self.assertEqual(self.client.get("/account").status_code, 302)
        self.assertEqual(self.client.post("/logout", data={"csrf_token": token}).status_code, 400)

    def test_logout_cannot_be_triggered_with_get(self):
        self.login()
        self.assertEqual(self.client.get("/logout").status_code, 405)
        self.assertEqual(self.client.get("/account").status_code, 200)

    def test_login_and_logout_require_csrf(self):
        self.assertEqual(self.client.post("/login", data={"email": "anar@example.com"}).status_code, 400)
        self.login()
        self.assertEqual(self.client.post("/logout").status_code, 400)
        self.assertEqual(self.client.get("/account").status_code, 200)

    def test_non_ascii_csrf_token_returns_bad_request_instead_of_server_error(self):
        response = self.login(csrf_token="буруу")
        self.assertEqual(response.status_code, 400)

    def test_deleted_user_session_cannot_access_account(self):
        self.login()
        with self.app.app_context():
            connection = get_db()
            with connection:
                connection.execute("DELETE FROM users WHERE id = ?", (self.user.id,))
        self.assertEqual(self.client.get("/account").status_code, 302)

    def test_browser_sessions_are_isolated(self):
        self.login()
        another_client = self.app.test_client()
        self.assertEqual(another_client.get("/account").status_code, 302)

    def test_session_cookie_and_private_response_headers(self):
        response = self.login()
        self.assertIn("HttpOnly", response.headers["Set-Cookie"])
        self.assertIn("SameSite=Lax", response.headers["Set-Cookie"])
        account = self.client.get("/account")
        self.assertEqual(account.headers["Cache-Control"], "no-store")
        self.assertEqual(account.headers["X-Frame-Options"], "DENY")

    def test_complete_registration_login_logout_flow(self):
        self.client.post(
            "/register",
            data={
                "full_name": "Хүслэн",
                "email": "huslen@example.com",
                "password": "AnotherPass123!",
                "csrf_token": self.token(),
            },
        )
        response = self.login(email="huslen@example.com", password="AnotherPass123!")
        self.assertEqual(response.status_code, 303)
        account = self.client.get("/account")
        self.assertIn("Хүслэн", account.text)
        self.assertNotIn("anar@example.com", account.text)
        with self.client.session_transaction() as session:
            token = session["csrf_token"]
        self.client.post("/logout", data={"csrf_token": token})
        self.assertEqual(self.client.get("/account").status_code, 302)


if __name__ == "__main__":
    unittest.main()
