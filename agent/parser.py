def parse_single_command(user_input: str) -> dict:
    text = user_input.lower().strip()

    if text == "active window":
        return {"intent": "active_window"}

    if text == "list windows":
        return {"intent": "list_windows"}

    if text == "new tab":
        return {"intent": "new_tab"}

    if text == "close tab":
        return {"intent": "close_tab"}

    if text == "focus address bar":
        return {"intent": "focus_address_bar"}

    if text == "quick open":
        return {"intent": "quick_open"}

    if text == "command palette":
        return {"intent": "command_palette"}

    if text == "chrome new tab":
        return {"intent": "chrome_new_tab"}

    if text == "chrome address bar":
        return {"intent": "chrome_address_bar"}

    if text == "vscode quick open":
        return {"intent": "vscode_quick_open"}

    if text == "vscode command palette":
        return {"intent": "vscode_command_palette"}

    if text.startswith("focus "):
        return {"intent": "focus_window", "target": user_input[6:].strip()}

    if text == "open my last project":
        return {"intent": "open_last_project"}

    if text == "list projects":
        return {"intent": "list_projects"}

    if text.startswith("save project "):
        return {"intent": "save_project", "path": user_input[13:].strip()}

    if text.startswith("open "):
        remainder = user_input[5:].strip()

        if remainder.isdigit():
            return {"intent": "open_by_index", "index": int(remainder)}

        return {"intent": "open_app", "target": remainder}

    if text.startswith("find "):
        return {"intent": "find_file", "query": user_input[5:].strip()}

    if text.startswith("create file "):
        return {"intent": "create_file", "name": user_input[12:].strip()}

    if text.startswith("summarize file "):
        return {"intent": "summarize_file", "path": user_input[15:].strip()}

    return {"intent": "unknown", "raw": user_input}


def parse_command(user_input: str):
    text = user_input.strip()

    separators = [" and ", " then "]

    for sep in separators:
        if sep in text.lower():
            parts = []
            remaining = text
            lower_remaining = remaining.lower()
            lower_sep = sep.lower()

            start = 0
            while True:
                idx = lower_remaining.find(lower_sep, start)
                if idx == -1:
                    parts.append(remaining[start:].strip())
                    break
                parts.append(remaining[start:idx].strip())
                start = idx + len(sep)

            return [parse_single_command(part) for part in parts if part.strip()]

    return parse_single_command(user_input)