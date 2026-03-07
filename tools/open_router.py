from tools.apps import search_apps, open_app
from tools.projects import search_projects, open_project_path
from tools.files import search_file_matches, open_file_path
from tools.session import LAST_OPEN_MATCHES


def score_match(query: str, name: str, match_type: str) -> int:
    query = query.lower().strip()
    name = name.lower().strip()

    score = 0

    if name == query:
        score += 100
    elif name.startswith(query):
        score += 80
    elif query in name.split():
        score += 60
    elif query in name:
        score += 40

    if match_type == "app":
        score += 15
    elif match_type == "project":
        score += 10

    return score


def smart_open(target: str) -> str:
    app_matches = search_apps(target)
    project_matches = search_projects(target)
    file_matches = search_file_matches(target, limit=10)

    all_matches = app_matches + project_matches + file_matches

    if not all_matches:
        return f"I couldn't find any app, project, or file matching '{target}'."

    ranked_matches = sorted(
        all_matches,
        key=lambda match: score_match(target, match["name"], match["type"]),
        reverse=True
    )

    # If there is only one result, open it immediately
    if len(ranked_matches) == 1:
        return open_match(ranked_matches[0])

    best_score = score_match(target, ranked_matches[0]["name"], ranked_matches[0]["type"])
    second_score = score_match(target, ranked_matches[1]["name"], ranked_matches[1]["type"])

    # Auto-open if the best result is clearly stronger
    if best_score >= 80 and (best_score - second_score) >= 20:
        return open_match(ranked_matches[0])

    LAST_OPEN_MATCHES.clear()
    LAST_OPEN_MATCHES.extend(ranked_matches)

    lines = []
    for i, match in enumerate(ranked_matches, start=1):
        lines.append(f"{i}. [{match['type']}] {match['name']} -> {match['value']}")

    return "I found multiple matches:\n" + "\n".join(lines) + "\n\nType: open 1"


def open_match(match: dict) -> str:
    match_type = match["type"]
    value = match["value"]

    if match_type == "app":
        return open_app(value)

    if match_type == "project":
        return open_project_path(value)

    if match_type == "file":
        return open_file_path(value)

    return f"Unknown match type: {match_type}"


def open_match_by_index(index: int) -> str:
    if not LAST_OPEN_MATCHES:
        return "No previous match list found. Try 'open something' first."

    if index < 1 or index > len(LAST_OPEN_MATCHES):
        return f"Invalid selection number. Choose between 1 and {len(LAST_OPEN_MATCHES)}."

    match = LAST_OPEN_MATCHES[index - 1]
    return open_match(match)