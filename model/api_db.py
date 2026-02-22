import sqlite3
from flask import g

DATABASE = "erlantzi_es_un_txapuzas.db"


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


def delete_combo(trigger_content, response_content):
    db = get_db()
    c = db.cursor()

    # Log the inputs (use !r to show hidden characters like spaces, quotes, etc.)
    print(f"[DEBUG] Inputs: trigger='{trigger_content!r}', response='{response_content!r}'")

    # Get all triggers matching the input (to check for duplicates)
    c.execute("SELECT idTrigger, content FROM trigger WHERE content LIKE ?", (trigger_content,))
    trigger_rows = c.fetchall()
    print(f"[DEBUG] Found triggers for '{trigger_content}':")
    for row in trigger_rows:
        print(f"  - ID: {row['idTrigger']}, Content: '{row['content']!r}'")

    # Get all responses matching the input (to check for duplicates)
    c.execute("SELECT idResponse, content FROM response WHERE content LIKE ?", (response_content,))
    response_rows = c.fetchall()
    print(f"[DEBUG] Found responses for '{response_content}':")
    for row in response_rows:
        print(f"  - ID: {row['idResponse']}, Content: '{row['content']!r}'")

    # Get the first trigger and response (if they exist)
    trigger_row = trigger_rows[0] if trigger_rows else None
    response_row = response_rows[0] if response_rows else None

    # Log the IDs being used for deletion
    if trigger_row and response_row:
        print(f"[DEBUG] Using IDs: trigger_id={trigger_row['idTrigger']}, response_id={response_row['idResponse']}")

        # Check if the combo exists
        c.execute(
            "SELECT * FROM combo WHERE idTrigger = ? AND idResponse = ?",
            (trigger_row["idTrigger"], response_row["idResponse"])
        )
        combo_row = c.fetchone()
        print(f"[DEBUG] Combo exists: {combo_row is not None}")
        if combo_row:
            print(f"[DEBUG] Combo details: {combo_row}")
    else:
        print("[DEBUG] No trigger or response found. Cannot delete.")

def delete_combo(trigger_content, response_content):
    db = get_db()
    c = db.cursor()

    print(f"[DEBUG] Inputs: trigger='{trigger_content!r}', response='{response_content!r}'")

    # Get all trigger IDs for the given content
    c.execute("SELECT idTrigger FROM trigger WHERE content = ?", (trigger_content,))
    trigger_ids = [row["idTrigger"] for row in c.fetchall()]
    print(f"[DEBUG] Found trigger IDs: {trigger_ids}")

    # Get all response IDs for the given content
    c.execute("SELECT idResponse FROM response WHERE content = ?", (response_content,))
    response_ids = [row["idResponse"] for row in c.fetchall()]
    print(f"[DEBUG] Found response IDs: {response_ids}")

    # Delete all combos that match any of the trigger/response IDs
    deleted_rows = 0
    for trigger_id in trigger_ids:
        for response_id in response_ids:
            c.execute(
                "DELETE FROM combo WHERE idTrigger = ? AND idResponse = ?",
                (trigger_id, response_id)
            )
            deleted_rows += c.rowcount

    db.commit()
    print(f"[DEBUG] Total rows deleted: {deleted_rows}")
    return deleted_rows




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


def new_user(username, password_hash):
    db = get_db()
    c = db.cursor()
    c.execute(
        "INSERT INTO user (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    db.commit()
    return c.lastrowid