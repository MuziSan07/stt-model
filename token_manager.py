# token_manager.py

from db import get_db
from datetime import datetime, timedelta
import uuid
import secrets

def create_token(name):
    conn = get_db()
    cursor = conn.cursor()
    token_id = str(uuid.uuid4())
    token_value = secrets.token_hex(16)  # Securely generated token
    now = datetime.now()
    expires = now + timedelta(days=365)  # Token expires in one year
    cursor.execute('''
        INSERT INTO tokens (id, name, token, status, created_on, expires_on, last_used)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (token_id, name, token_value, "active", now.date(), expires.date(), "Never"))
    conn.commit()

def get_all_tokens():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tokens")
    return cursor.fetchall()

def revoke_token(token_id):
    conn = get_db()
    conn.execute("UPDATE tokens SET status = 'revoked' WHERE id = ?", (token_id,))
    conn.commit()

def restore_token(token_id):
    conn = get_db()
    conn.execute("UPDATE tokens SET status = 'active' WHERE id = ?", (token_id,))
    conn.commit()

def renew_token(token_id):
    new_expiry = (datetime.now() + timedelta(days=365)).date()
    conn = get_db()
    conn.execute("UPDATE tokens SET expires_on = ? WHERE id = ?", (new_expiry, token_id))
    conn.commit()

def delete_token(token_id):
    conn = get_db()
    conn.execute("DELETE FROM tokens WHERE id = ?", (token_id,))
    conn.commit()

def get_token_by_id(token_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tokens WHERE id = ?", (token_id,))
    return cursor.fetchone()

def get_token_by_value(token: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tokens WHERE token = ?", (token,))
    return cursor.fetchone()

def update_token_usage(token_id):
    now = datetime.now().date()
    conn = get_db()
    conn.execute("UPDATE tokens SET last_used = ? WHERE id = ?", (now, token_id))
    conn.commit()
