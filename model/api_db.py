import sqlite3
from flask import g

DATABASE = "TelekApp/erlantzi_es_un_txapuzas.db"


# =========================
# Database Connection
# =========================

def get_db():
    """
    Returns a request-scoped SQLite connection.
    """
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.execute("PRAGMA foreign_keys = ON;")
        g.db.row_factory = sqlite3.Row  # Optional: enables dict-style access
    return g.db


def close_db(e=None):
    """
    Closes the database connection at the end of the request.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


# =========================
# Query Functions
# =========================

def get_combos(trigger_content=None):
    db = get_db()
    c = db.cursor()

    base_query = """
        SELECT 
            t.content AS trigger_content,
            r.content AS response_content
        FROM combo c
        JOIN trigger t ON c.idTrigger = t.idTrigger
        JOIN response r ON c.idResponse = r.idResponse
    """

    params = ()

    if trigger_content:
        base_query += " WHERE t.content = ?"
        params = (trigger_content,)

    base_query += " ORDER BY t.idTrigger;"

    c.execute(base_query, params)
    rows = c.fetchall()

    result = {}

    for row in rows:
        trig = row["trigger_content"]
        resp = row["response_content"]

        if trig not in result:
            result[trig] = {
                "trigger": trig,
                "responses": []
            }

        result[trig]["responses"].append(resp)

    if trigger_content:
        return result.get(trigger_content)

    return list(result.values())


# =========================
# Insert Functions
# =========================

def create_trigger(trigger):
    db = get_db()
    c = db.cursor()
    c.execute("INSERT INTO trigger (content) VALUES (?)", (trigger,))
    db.commit()
    return c.lastrowid


def create_response(response):
    db = get_db()
    c = db.cursor()
    c.execute("INSERT INTO response (content) VALUES (?)", (response,))
    db.commit()
    return c.lastrowid


def create_combo(trigger_id, response_id):
    db = get_db()
    c = db.cursor()
    c.execute(
        "INSERT INTO combo (idTrigger, idResponse) VALUES (?, ?)",
        (trigger_id, response_id)
    )
    db.commit()
    return c.lastrowid


def delete_combo(trigger_id, response_id):
    db = get_db()
    c = db.cursor()
    c.execute(
        "DELETE FROM combo WHERE idTrigger = (SELECT idTrigger FROM trigger WHERE content = ?) AND idResponse = (SELECT idResponse FROM response WHERE content = ?)",
        (trigger_id, response_id)
    )
    db.commit()
    return c.rowcount  # number of rows deleted


def authenticate(username, password_hash):
    db = get_db()
    c = db.cursor()
    c.execute(
        "SELECT id FROM user WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    row = c.fetchone()
    if row:
        return True
    return None
