import sqlite3
from pathlib import Path

DB_PATH = Path("memory.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS command_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT,
        intent TEXT,
        result TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recent_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT,
        project_path TEXT UNIQUE,
        last_opened DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def log_command(user_input: str, intent: str, result: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO command_history (user_input, intent, result)
    VALUES (?, ?, ?)
    """, (user_input, intent, result))

    conn.commit()
    conn.close()


def save_project(project_path: str) -> str:
    path = Path(project_path)

    if not path.exists() or not path.is_dir():
        return f"Invalid project folder: {project_path}"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO recent_projects (project_name, project_path, last_opened)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(project_path) DO UPDATE SET
        last_opened = CURRENT_TIMESTAMP
    """, (path.name, str(path)))

    conn.commit()
    conn.close()

    return f"Saved project: {path.name}"


def get_last_project():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT project_name, project_path
    FROM recent_projects
    ORDER BY last_opened DESC
    LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return row


def list_projects():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT project_name, project_path, last_opened
    FROM recent_projects
    ORDER BY last_opened DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows

def find_project_by_name(name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT project_name, project_path
    FROM recent_projects
    WHERE LOWER(project_name) LIKE ?
    ORDER BY last_opened DESC
    LIMIT 1
    """, (f"%{name.lower()}%",))

    row = cursor.fetchone()
    conn.close()

    return row

def search_projects_by_name(name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT project_name, project_path
    FROM recent_projects
    WHERE LOWER(project_name) LIKE ?
    ORDER BY last_opened DESC
    """, (f"%{name.lower()}%",))

    rows = cursor.fetchall()
    conn.close()

    return rows