import sqlite3
from datetime import datetime, timedelta
import uuid
import secrets

DB_PATH = "tokens.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS tokens (
            id TEXT PRIMARY KEY,
            token TEXT,
            status TEXT,
            created_on TEXT,
            expires_on TEXT
        )
    ''')
    conn.commit()

def create_token(name: str):
    conn = get_db()
    cursor = conn.cursor()
    token = str(uuid.uuid4())
    created_on = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    expires_on = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO tokens (id, token, status, created_on, expires_on)
        VALUES (?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), token, 'active', created_on, expires_on))
    conn.commit()
    return token

def revoke_token(token_id: str):
    conn = get_db()
    conn.execute("UPDATE tokens SET status = 'revoked' WHERE id = ?", (token_id,))
    conn.commit()

def renew_token(token_id: str):
    new_expiry = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db()
    conn.execute("UPDATE tokens SET expires_on = ? WHERE id = ?", (new_expiry, token_id))
    conn.commit()

def get_token_by_value(token: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tokens WHERE token = ?", (token,))
    return cursor.fetchone()

def delete_token(token_id: str):
    conn = get_db()
    conn.execute("DELETE FROM tokens WHERE id = ?", (token_id,))
    conn.commit()

