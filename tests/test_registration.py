"""US-01 acceptance tests against the real service and SQLite repository."""

import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from werkzeug.security import check_password_hash

from bike_sharing import create_app
from bike_sharing.auth import AuthService, ValidationError
from bike_sharing.db import get_db


class RegistrationTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.app = create_app(
            {"TESTING": True, "SECRET_KEY": "test-only", "DATABASE": str(Path(self.directory.name) / "test.db")}
        )
        self.context = self.app.app_context()
        self.context.push()
        self.addCleanup(self.context.pop)
        self.service = AuthService(get_db())

    def test_registers_and_persists_user_without_plaintext_password(self):
        user = self.service.register("Ө. Анар", "Anar@Example.com", "BikePass123!")
        stored = get_db().execute("SELECT * FROM users WHERE id = ?", (user.id,)).fetchone()
        self.assertEqual(stored["full_name"], "Ө. Анар")
        self.assertEqual(stored["email"], "anar@example.com")
        self.assertNotEqual(stored["password_hash"], "BikePass123!")
        self.assertTrue(check_password_hash(stored["password_hash"], "BikePass123!"))
        self.assertNotIn("password", vars(user))
        self.assertNotIn("password_hash", vars(user))

    def test_duplicate_email_is_rejected_case_insensitively(self):
        self.service.register("Анар", "anar@example.com", "BikePass123!")
        with self.assertRaises(ValidationError):
            self.service.register("Өөр нэр", " ANAR@example.com ", "OtherPass123!")
        self.assertEqual(get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0], 1)

    def test_invalid_inputs_do_not_create_users(self):
        invalid = [
            ("", "anar@example.com", "BikePass123!"),
            ("A", "anar@example.com", "BikePass123!"),
            ("A" * 81, "anar@example.com", "BikePass123!"),
            ("Анар\nАдмин", "anar@example.com", "BikePass123!"),
            ("Анар", "wrong", "BikePass123!"),
            ("Анар", "a@@example.com", "BikePass123!"),
            ("Анар", "a b@example.com", "BikePass123!"),
            ("Анар", "a" * 250 + "@example.com", "BikePass123!"),
            ("Анар", "anar@example.com", "1234567"),
            ("Анар", "anar@example.com", " " * 8),
            ("Анар", "anar@example.com", "x" * 129),
            ("Анар", "anar@example.com", "pass\x00word"),
            (None, "anar@example.com", "BikePass123!"),
            ("Анар", None, "BikePass123!"),
            ("Анар", "anar@example.com", None),
        ]
        for values in invalid:
            with self.subTest(values=values[:2]), self.assertRaises(ValidationError):
                self.service.register(*values)
        self.assertEqual(get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0], 0)

    def test_password_boundaries_and_whitespace_are_preserved(self):
        for index, password in enumerate(["12345678", "x" * 128, "  secret  "]):
            with self.subTest(length=len(password)):
                user = self.service.register("Анар", f"u{index}@example.com", password)
                row = get_db().execute("SELECT password_hash FROM users WHERE id = ?", (user.id,)).fetchone()
                self.assertTrue(check_password_hash(row[0], password))

    def test_sql_text_in_name_is_stored_as_data(self):
        name = "Robert'); DROP TABLE users;--"
        user = self.service.register(name, "anar@example.com", "BikePass123!")
        self.assertEqual(get_db().execute("SELECT full_name FROM users WHERE id = ?", (user.id,)).fetchone()[0], name)

    def test_concurrent_duplicate_registration_creates_exactly_one_user(self):
        def register():
            with self.app.app_context():
                try:
                    AuthService(get_db()).register("Анар", "same@example.com", "BikePass123!")
                    return "created"
                except ValidationError:
                    return "duplicate"

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: register(), range(2)))
        self.assertCountEqual(results, ["created", "duplicate"])

    def test_account_survives_new_application_instance(self):
        self.service.register("Анар", "anar@example.com", "BikePass123!")
        another_app = create_app(dict(self.app.config))
        with another_app.app_context():
            self.assertEqual(get_db().execute("SELECT email FROM users").fetchone()[0], "anar@example.com")


if __name__ == "__main__":
    unittest.main()
