"""Parameterized database operations; secrets never leave the repository/service."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    full_name: str
    email: str


class UserRepository:
    def __init__(self, connection):
        self.connection = connection

    def create(self, full_name, email, password_hash):
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                (full_name, email, password_hash),
            )
        return User(cursor.lastrowid, full_name, email)

    def find_credentials(self, email):
        return self.connection.execute(
            "SELECT id, full_name, email, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()

    def find_by_id(self, user_id):
        row = self.connection.execute("SELECT id, full_name, email FROM users WHERE id = ?", (user_id,)).fetchone()
        return User(**dict(row)) if row else None
