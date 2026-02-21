import sqlite3
import random

DB_PATH = "TelekApp/erlantzi_es_un_txapuzas.db"

def get_combos(trigger_content=None):
    """
    Returns combos from SQLite DB.
    Works in any thread/process.
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


def get_random_response(trigger_content):
    combo = get_combos(trigger_content)
    if combo and combo["responses"]:
        return random.choice(combo["responses"])
    return None