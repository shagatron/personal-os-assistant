import os
from tools.memory import (
    get_last_project,
    save_project,
    list_projects,
    find_project_by_name,
    search_projects_by_name,
)


def save_project_folder(project_path: str) -> str:
    return save_project(project_path)


def open_last_project() -> str:
    project = get_last_project()

    if not project:
        return "No recent project saved yet."

    project_name, project_path = project

    try:
        os.startfile(project_path)
        return f"Opened last project: {project_name}\n{project_path}"
    except Exception as e:
        return f"Found project but failed to open it: {e}"


def open_project_by_name(name: str):
    project = find_project_by_name(name)

    if not project:
        return None

    project_name, project_path = project

    try:
        os.startfile(project_path)
        return f"Opened project: {project_name}\n{project_path}"
    except Exception as e:
        return f"Found project but failed to open it: {e}"


def search_projects(query: str):
    rows = search_projects_by_name(query)

    matches = []
    for project_name, project_path in rows:
        matches.append({
            "type": "project",
            "name": project_name,
            "value": project_path
        })

    return matches


def open_project_path(project_path: str):
    try:
        os.startfile(project_path)
        return f"Opened project:\n{project_path}"
    except Exception as e:
        return f"Could not open project:\n{project_path}\nError: {e}"


def show_projects() -> str:
    projects = list_projects()

    if not projects:
        return "No saved projects yet."

    lines = []
    for name, path, last_opened in projects:
        lines.append(f"{name} -> {path} ({last_opened})")

    return "Saved projects:\n" + "\n".join(lines)