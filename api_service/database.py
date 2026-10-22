
import hashlib
import hmac
import os
import secrets
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "users.db"

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
HASH_LENGTH = 64


def get_connection():
    """Open a connection to the local user database."""
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the users table if it does not already exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'admin'))
            )
        """)


def hash_password(password, salt=None):
    """Return a random salt and a scrypt password hash."""
    if salt is None:
        salt = secrets.token_bytes(16)

    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=HASH_LENGTH,
    )

    return salt.hex(), password_hash.hex()



def verify_password(password, salt_hex, expected_hash_hex):
    try:
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(expected_hash_hex)
    except (TypeError, ValueError):
        return False

    if len(salt) != 16 or len(expected_hash) != HASH_LENGTH:
        return False

    _, calculated_hash_hex = hash_password(password, salt)

    return hmac.compare_digest(
        calculated_hash_hex,
        expected_hash_hex,
    )



def create_user(username, password, role):
    """Create an account, without overwriting an existing account."""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("Username must not be empty.")

    if not isinstance(password, str) or len(password) < 12:
        raise ValueError("Password must contain at least 12 characters.")

    if role not in {"user", "admin"}:
        raise ValueError("Role must be 'user' or 'admin'.")

    salt_hex, password_hash_hex = hash_password(password)

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (username, password_salt, password_hash, role)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(username) DO NOTHING
            """,
            (username.strip(), salt_hex, password_hash_hex, role),
        )


def get_user_by_username(username):
    """Return a user's database row, or None if the user doesn't exist."""
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT username, password_salt, password_hash, role
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()
