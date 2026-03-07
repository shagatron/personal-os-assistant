from pathlib import Path
import os

SEARCH_ROOTS = [
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.cwd(),
]

IGNORED_DIRS = {
    "venv",
    "__pycache__",
    "node_modules",
    ".git",
    "Microsoft VS Code",
}


def search_files(query: str, limit: int = 10):
    query = query.lower().strip()
    matches = []

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if any(part in IGNORED_DIRS for part in path.parts):
                continue

            if path.is_file() and query in path.name.lower():
                matches.append(path)

                if len(matches) >= limit:
                    return matches

    return matches


def search_file_matches(query: str, limit: int = 10):
    paths = search_files(query, limit=limit)

    matches = []
    for path in paths:
        matches.append({
            "type": "file",
            "name": path.name,
            "value": str(path)
        })

    return matches


def find_file(query: str) -> str:
    matches = search_files(query)

    if not matches:
        return f"No files found matching '{query}'."

    lines = [f"{i + 1}. {path}" for i, path in enumerate(matches)]
    return "Found files:\n" + "\n".join(lines)


def open_file_path(file_path: str) -> str:
    try:
        os.startfile(file_path)
        return f"Opened file:\n{file_path}"
    except Exception as e:
        return f"Could not open file:\n{file_path}\nError: {e}"


def create_file(name: str) -> str:
    try:
        file_path = Path.cwd() / name
        file_path.touch(exist_ok=True)
        return f"Created file: {file_path}"
    except Exception as e:
        return f"Failed to create file: {e}"


def summarize_file(path_str: str) -> str:
    path = Path(path_str)

    if not path.exists():
        return "File not found."

    if path.suffix.lower() not in [".txt", ".md"]:
        return "Only .txt and .md supported for summarization right now."

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Could not read file: {e}"

    if len(content) <= 300:
        return content

    return content[:300] + "..."