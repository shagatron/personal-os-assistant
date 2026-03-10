import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("memory.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS command_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT NOT NULL,
        intent TEXT NOT NULL,
        result TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS saved_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        path TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS workflow_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command TEXT NOT NULL UNIQUE,
        intent TEXT NOT NULL,
        params TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# -------------------------
# Command history
# -------------------------

def log_command(user_input: str, intent: str, result: str) -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO command_history (user_input, intent, result)
    VALUES (?, ?, ?)
    """, (user_input, intent, result))

    conn.commit()
    conn.close()


def get_command_history(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, user_input, intent, result, created_at
    FROM command_history
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# -------------------------
# Projects
# -------------------------

def save_project(name: str, path: str) -> str:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT id FROM saved_projects WHERE LOWER(name) = LOWER(?)
    """, (name,))
    existing = cur.fetchone()

    if existing:
        cur.execute("""
        UPDATE saved_projects
        SET path = ?
        WHERE id = ?
        """, (path, existing["id"]))
        message = f"Updated project '{name}'"
    else:
        cur.execute("""
        INSERT INTO saved_projects (name, path)
        VALUES (?, ?)
        """, (name, path))
        message = f"Saved project '{name}'"

    conn.commit()
    conn.close()
    return message


def list_projects() -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, name, path, created_at
    FROM saved_projects
    ORDER BY created_at DESC, id DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_last_project() -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, name, path, created_at
    FROM saved_projects
    ORDER BY created_at DESC, id DESC
    LIMIT 1
    """)

    row = cur.fetchone()
    conn.close()

    return dict(row) if row else None


def search_projects_by_name(name: str) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, name, path, created_at
    FROM saved_projects
    WHERE LOWER(name) LIKE LOWER(?)
    ORDER BY name ASC
    """, (f"%{name}%",))

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def find_project_by_name(name: str) -> Optional[Dict[str, Any]]:
    matches = search_projects_by_name(name)
    return matches[0] if matches else None


def delete_project(name: str) -> str:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM saved_projects
    WHERE LOWER(name) = LOWER(?)
    """, (name,))

    deleted = cur.rowcount
    conn.commit()
    conn.close()

    if deleted:
        return f"Deleted project '{name}'"
    return f"No project found with name '{name}'"


# -------------------------
# Workflow cache
# -------------------------

def cache_workflow(command: str, intent: str, params: Dict[str, Any]) -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO workflow_cache (command, intent, params)
    VALUES (?, ?, ?)
    ON CONFLICT(command) DO UPDATE SET
        intent = excluded.intent,
        params = excluded.params
    """, (command.strip().lower(), intent, json.dumps(params)))

    conn.commit()
    conn.close()


def get_cached_workflow(command: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT command, intent, params, created_at
    FROM workflow_cache
    WHERE command = ?
    """, (command.strip().lower(),))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "command": row["command"],
        "intent": row["intent"],
        "params": json.loads(row["params"]),
        "created_at": row["created_at"],
    }


def list_cached_workflows() -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT command, intent, params, created_at
    FROM workflow_cache
    ORDER BY created_at DESC, id DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "command": row["command"],
            "intent": row["intent"],
            "params": json.loads(row["params"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def clear_workflow_cache() -> str:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM workflow_cache")
    conn.commit()
    conn.close()

    return "Workflow cache cleared"


# -------------------------
# Compatibility aliases
# -------------------------

def get_workflow(command: str) -> Optional[Dict[str, Any]]:
    return get_cached_workflow(command)


def save_workflow(command: str, intent: str, params: Dict[str, Any]) -> None:
    cache_workflow(command, intent, params)


def list_workflows() -> List[Dict[str, Any]]:
    return list_cached_workflows()


def clear_workflows() -> str:
    return clear_workflow_cache()


# -------------------------
# Startup
# -------------------------

init_db()