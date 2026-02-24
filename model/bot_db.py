import sqlite3
import random

DB_PATH = "erlantzi_es_un_txapuzas.db"

def get_combos(trigger_content=None):
    """
    Returns combos from SQLite DB.
    Works in any thread/process.

    Escondemos el vibe coding de mierdas web super bien
    
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = """
        SELECT t.content AS trigger_content,
               r.content AS response_content
        FROM combo c
        JOIN trigger t ON c.idTrigger = t.idTrigger
        JOIN response r ON c.idResponse = r.idResponse
    """

    params = ()
    if trigger_content:
        query += " WHERE t.content = ?"
        params = (trigger_content,)

    query += " ORDER BY t.idTrigger;"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

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

def get_trigger(trigger_content):
    # Ni de palo dejo pasar wildcards
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # NO TOCAR >.>
    query = """
        SELECT content
        FROM trigger
        WHERE LOWER(content) = LOWER(?)
        ORDER BY LENGTH(content) DESC
        LIMIT 1;
    """
    # NO TOCAR >.>
 
    c.execute(query, (trigger_content,))
    row = c.fetchone()
    conn.close()
    return row

def get_random_response(trigger_content):
    match = get_trigger(trigger_content)
    if match:
        # Get combos espera una string, no un objeto de sqlite
        combo = get_combos(match["content"])
        if combo and combo["responses"]:
            return random.choice(combo["responses"])
        return None
    return None
