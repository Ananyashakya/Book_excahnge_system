import mysql.connector
import bcrypt
import os
import re

# ─── CONFIG ───────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST",     "localhost"),
    "user":     os.environ.get("DB_USER",     "root"),
    "password": os.environ.get("DB_PASSWORD", "Mysql_123"),
    "database": "BookExchangeDB",
}

# ─── CONNECTION ───────────────────────────────────────────────────────────────
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ─── PASSWORD HELPERS (bcrypt) ────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """
    Bcrypt hash with auto-generated salt (cost factor 12).
    Each call produces a unique hash — always use verify_password() to compare,
    never a direct == check.
    """
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")   # stored as VARCHAR(256) in DB


def verify_password(plain: str, hashed: str) -> bool:
    """Securely compare a plain-text password against a stored bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))


# ─── SCHEMA SETUP ─────────────────────────────────────────────────────────────
def initialize_db():
    """Create tables if they don't exist and seed the admin account."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            name       VARCHAR(100) NOT NULL,
            email      VARCHAR(150) NOT NULL UNIQUE,
            password   VARCHAR(256) NOT NULL,
            is_admin   TINYINT(1) DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            title        VARCHAR(200) NOT NULL,
            author       VARCHAR(150) NOT NULL,
            genre        VARCHAR(100),
            condition_   VARCHAR(50) DEFAULT 'Good',
            owner_id     INT,
            is_available TINYINT(1) DEFAULT 1,
            listed_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            book_id       INT NOT NULL,
            requester_id  INT NOT NULL,
            owner_id      INT NOT NULL,
            status        ENUM('Pending','Approved','Rejected','Completed') DEFAULT 'Pending',
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id)      REFERENCES books(id),
            FOREIGN KEY (requester_id) REFERENCES users(id),
            FOREIGN KEY (owner_id)     REFERENCES users(id)
        )
    """)

    # Seed admin with bcrypt hash
    cursor.execute("SELECT id FROM users WHERE is_admin=1 LIMIT 1")
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (name, email, password, is_admin) VALUES (%s, %s, %s, %s)",
            ("Admin", "admin@bookexchange.com", hash_password("Admin@2025!"), 1)
        )

    conn.commit()
    conn.close()


# ─── USER OPERATIONS ──────────────────────────────────────────────────────────
def register_user(name: str, email: str, password: str):
    """Returns (True, user_id) or (False, error_message)."""
    if not is_valid_email(email):
        return False, "Invalid email format."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name.strip(), email.strip().lower(), hash_password(password))
        )
        conn.commit()
        return True, cursor.lastrowid
    except mysql.connector.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()


def authenticate_user(email: str, password: str):
    """
    Fetch user by email, then verify password using bcrypt.
    Returns user dict or None.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch the stored hash separately — bcrypt needs checkpw(), not SQL comparison
    cursor.execute(
        "SELECT id, name, email, password, is_admin FROM users WHERE email=%s",
        (email.strip().lower(),)
    )
    row = cursor.fetchone()
    conn.close()

    if row and verify_password(password, row["password"]):
        # Remove password hash before returning — never expose it to the UI
        row.pop("password")
        return row
    return None


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, email, is_admin, created_at FROM users ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# ─── BOOK OPERATIONS ──────────────────────────────────────────────────────────
def add_book(title: str, author: str, genre: str, condition: str, owner_id: int):
    """Returns (True, book_id) or (False, error_message)."""
    if not title.strip() or not author.strip():
        return False, "Title and author are required."
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (title, author, genre, condition_, owner_id) VALUES (%s,%s,%s,%s,%s)",
        (title.strip(), author.strip(), genre.strip(), condition, owner_id)
    )
    conn.commit()
    book_id = cursor.lastrowid
    conn.close()
    return True, book_id


def get_available_books(search: str = ""):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if search:
        like = f"%{search}%"
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.genre, b.condition_, u.name AS owner
            FROM books b
            JOIN users u ON b.owner_id = u.id
            WHERE b.is_available=1
              AND (b.title LIKE %s OR b.author LIKE %s OR b.genre LIKE %s)
            ORDER BY b.listed_at DESC
        """, (like, like, like))
    else:
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.genre, b.condition_, u.name AS owner
            FROM books b
            JOIN users u ON b.owner_id = u.id
            WHERE b.is_available=1
            ORDER BY b.listed_at DESC
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_user_books(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, title, author, genre, condition_, is_available, listed_at
        FROM books WHERE owner_id=%s ORDER BY listed_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_book(book_id: int, user_id: int, is_admin: bool = False):
    conn = get_connection()
    cursor = conn.cursor()
    if is_admin:
        cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
    else:
        cursor.execute(
            "DELETE FROM books WHERE id=%s AND owner_id=%s", (book_id, user_id)
        )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# ─── TRANSACTION OPERATIONS ───────────────────────────────────────────────────
def request_exchange(book_id: int, requester_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT owner_id, is_available FROM books WHERE id=%s", (book_id,))
    book = cursor.fetchone()
    if not book:
        conn.close()
        return False, "Book not found."
    if not book["is_available"]:
        conn.close()
        return False, "Book is no longer available."
    if book["owner_id"] == requester_id:
        conn.close()
        return False, "You cannot request your own book."

    cursor.execute(
        "INSERT INTO transactions (book_id, requester_id, owner_id) VALUES (%s,%s,%s)",
        (book_id, requester_id, book["owner_id"])
    )
    cursor.execute("UPDATE books SET is_available=0 WHERE id=%s", (book_id,))
    conn.commit()
    conn.close()
    return True, "Exchange request sent!"


def get_user_transactions(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.id, b.title, b.author,
               req.name AS requester, own.name AS owner,
               t.status, t.created_at
        FROM transactions t
        JOIN books b   ON t.book_id      = b.id
        JOIN users req ON t.requester_id = req.id
        JOIN users own ON t.owner_id     = own.id
        WHERE t.requester_id=%s OR t.owner_id=%s
        ORDER BY t.created_at DESC
    """, (user_id, user_id))
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_transaction_status(transaction_id: int, status: str, book_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE transactions SET status=%s WHERE id=%s", (status, transaction_id)
    )
    if status in ("Rejected", "Completed"):
        cursor.execute("UPDATE books SET is_available=1 WHERE id=%s", (book_id,))
    conn.commit()
    conn.close()


def get_all_transactions():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.id, b.title, b.author,
               req.name AS requester, own.name AS owner,
               t.status, t.created_at
        FROM transactions t
        JOIN books b   ON t.book_id      = b.id
        JOIN users req ON t.requester_id = req.id
        JOIN users own ON t.owner_id     = own.id
        ORDER BY t.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows