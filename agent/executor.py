from tools.open_router import smart_open, open_match_by_index
from tools.files import find_file, create_file, summarize_file
from tools.projects import save_project_folder, open_last_project, show_projects
from tools.windows import focus_window, list_open_windows, get_active_window
from tools.shortcuts import (
    send_new_tab,
    send_close_tab,
    send_focus_address_bar,
    send_quick_open,
    send_command_palette,
)


def execute_command(command: dict) -> str:
    intent = command.get("intent")

    if intent == "open_app":
        return smart_open(command["target"])

    if intent == "open_by_index":
        return open_match_by_index(command["index"])

    if intent == "focus_window":
        return focus_window(command["target"])

    if intent == "list_windows":
        return list_open_windows()

    if intent == "active_window":
        return get_active_window()

    if intent == "new_tab":
        return send_new_tab()

    if intent == "close_tab":
        return send_close_tab()

    if intent == "focus_address_bar":
        return send_focus_address_bar()

    if intent == "quick_open":
        return send_quick_open()

    if intent == "command_palette":
        return send_command_palette()

    if intent == "chrome_new_tab":
        focus_result = focus_window("chrome")
        action_result = send_new_tab()
        return f"{focus_result}\n{action_result}"

    if intent == "chrome_address_bar":
        focus_result = focus_window("chrome")
        action_result = send_focus_address_bar()
        return f"{focus_result}\n{action_result}"

    if intent == "vscode_quick_open":
        focus_result = focus_window("code")
        action_result = send_quick_open()
        return f"{focus_result}\n{action_result}"

    if intent == "vscode_command_palette":
        focus_result = focus_window("code")
        action_result = send_command_palette()
        return f"{focus_result}\n{action_result}"

    if intent == "find_file":
        return find_file(command["query"])

    if intent == "create_file":
        return create_file(command["name"])

    if intent == "summarize_file":
        return summarize_file(command["path"])

    if intent == "save_project":
        return save_project_folder(command["path"])

    if intent == "open_last_project":
        return open_last_project()

    if intent == "list_projects":
        return show_projects()

    return f"Sorry, I don't understand that command yet: {command}"