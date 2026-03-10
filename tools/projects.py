import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from tools.memory import (
    save_project,
    get_last_project,
    list_projects,
    search_projects_by_name,
    find_project_by_name,
)


def normalize_path(path: str) -> str:
    return str(Path(path).expanduser().resolve())


def path_exists(path: str) -> bool:
    return Path(path).exists()


def open_project_path(path: str) -> str:
    path = normalize_path(path)

    if not path_exists(path):
        return f"Project path does not exist: {path}"

    try:
        os.startfile(path)
        return f"Opened project: {path}"
    except Exception as e:
        return f"Failed to open project: {e}"


def open_project_in_vscode(path: str) -> str:
    path = normalize_path(path)

    if not path_exists(path):
        return f"Project path does not exist: {path}"

    try:
        subprocess.Popen(["code", path], shell=True)
        return f"Opened project in VS Code: {path}"
    except Exception as e:
        return f"Failed to open project in VS Code: {e}"


def save_current_project(name: str, path: str) -> str:
    path = normalize_path(path)
    return save_project(name, path)


def save_project_folder(name: str, path: str) -> str:
    """
    Alias kept for compatibility with executor.py
    """
    return save_current_project(name, path)


def open_last_project() -> str:
    project = get_last_project()

    if not project:
        return "No saved projects found"

    return open_project_path(project["path"])


def open_last_project_in_vscode() -> str:
    project = get_last_project()

    if not project:
        return "No saved projects found"

    return open_project_in_vscode(project["path"])


def get_projects_text() -> str:
    projects = list_projects()

    if not projects:
        return "No saved projects found"

    lines = []
    for i, project in enumerate(projects, start=1):
        lines.append(f"{i}. {project['name']} -> {project['path']}")

    return "\n".join(lines)


def show_projects() -> str:
    """
    Alias kept for compatibility with executor.py
    """
    return get_projects_text()


def search_projects(query: str) -> List[Dict]:
    return search_projects_by_name(query)


def search_projects_text(query: str) -> str:
    matches = search_projects_by_name(query)

    if not matches:
        return f"No projects found matching '{query}'"

    lines = []
    for i, project in enumerate(matches, start=1):
        lines.append(f"{i}. {project['name']} -> {project['path']}")

    return "\n".join(lines)


def open_project_by_name(name: str) -> str:
    project = find_project_by_name(name)

    if not project:
        return f"No project found matching '{name}'"

    return open_project_path(project["path"])


def open_project_by_name_in_vscode(name: str) -> str:
    project = find_project_by_name(name)

    if not project:
        return f"No project found matching '{name}'"

    return open_project_in_vscode(project["path"])


def open_project_match_by_index(query: str, index: int) -> str:
    matches = search_projects_by_name(query)

    if not matches:
        return f"No projects found matching '{query}'"

    if index < 1 or index > len(matches):
        return f"Invalid selection. Choose between 1 and {len(matches)}"

    project = matches[index - 1]
    return open_project_path(project["path"])


def open_project_match_by_index_in_vscode(query: str, index: int) -> str:
    matches = search_projects_by_name(query)

    if not matches:
        return f"No projects found matching '{query}'"

    if index < 1 or index > len(matches):
        return f"Invalid selection. Choose between 1 and {len(matches)}"

    project = matches[index - 1]
    return open_project_in_vscode(project["path"])