import sqlite3
from datetime import datetime
from contextlib import contextmanager

DATABASE_URL = "documents.db"

def init_db():
    with get_db() as db:
        db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT,
            email TEXT
        )
        ''')

        db.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            document_name TEXT NOT NULL,
            document_type TEXT NOT NULL,
            upload_date TIMESTAMP NOT NULL,
            status TEXT NOT NULL,
            risk_level TEXT,
            report_data TEXT,  -- This will store the complete analysis response
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Insert default users
        users = [
            ('admin', 'adminpass123', 'Admin User', 'admin@example.com'),
            ('user1', 'user1pass', 'User One', 'user1@example.com'),
            ('user2', 'user2pass', 'User Two', 'user2@example.com'),
            ('user3', 'user3pass', 'User Three', 'user3@example.com'),
            ('user4', 'user4pass', 'User Four', 'user4@example.com'),
        ]
        
        for user in users:
            try:
                db.execute('''
                INSERT INTO users (username, hashed_password, full_name, email)
                VALUES (?, ?, ?, ?)
                ''', user)
            except sqlite3.IntegrityError:
                # Skip if user already exists
                pass

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()