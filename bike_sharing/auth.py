"""US-01 business rules, independent from HTTP forms and templates."""

import re
import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from .repository import User, UserRepository

EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+"
)
LOGIN_ERROR = "Цахим шуудан эсвэл нууц үг буруу байна."
# Unknown accounts also perform password hashing instead of returning immediately.
DUMMY_HASH = generate_password_hash("not-a-real-account-password", method="scrypt")


class ValidationError(ValueError):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


def normalize_email(email):
    if not isinstance(email, str):
        raise ValidationError("Цахим шуудангаа зөв оруулна уу.")
    normalized = email.strip().lower()
    if len(normalized) > 254 or not EMAIL_PATTERN.fullmatch(normalized):
        raise ValidationError("Цахим шуудангаа зөв оруулна уу.")
    return normalized


class AuthService:
    def __init__(self, connection):
        self.users = UserRepository(connection)

    def register(self, full_name, email, password):
        if not isinstance(full_name, str) or any(ord(char) < 32 for char in full_name):
            raise ValidationError("Нэрээ зөв оруулна уу.")
        full_name = full_name.strip()
        if not 2 <= len(full_name) <= 80:
            raise ValidationError("Нэр 2-80 тэмдэгттэй байна.")
        email = normalize_email(email)
        if not isinstance(password, str) or not 8 <= len(password) <= 128 or not password.strip() or "\x00" in password:
            raise ValidationError("Нууц үг 8-128 тэмдэгттэй, дан хоосон зай биш байна.")
        password_hash = generate_password_hash(password, method="scrypt")
        try:
            return self.users.create(full_name, email, password_hash)
        except sqlite3.IntegrityError as error:
            raise ValidationError("Энэ цахим шуудан бүртгэлтэй байна.", 409) from error

    def login(self, email, password):
        try:
            email = normalize_email(email)
        except ValidationError as error:
            raise ValidationError(LOGIN_ERROR, 401) from error
        if not isinstance(password, str) or not 1 <= len(password) <= 128 or "\x00" in password:
            raise ValidationError(LOGIN_ERROR, 401)
        row = self.users.find_credentials(email)
        matches = check_password_hash(row["password_hash"] if row else DUMMY_HASH, password)
        if row is None or not matches:
            raise ValidationError(LOGIN_ERROR, 401)
        return User(row["id"], row["full_name"], row["email"])
