from tools.open_router import smart_open, open_match_by_index
from tools.files import find_file, create_file, summarize_file
from tools.projects import save_project_folder, open_last_project, show_projects
from tools.windows import focus_window, list_open_windows, get_active_window
from tools.ide import vscode_open_file, vscode_search, vscode_new_file
from tools.shortcuts import (
    send_new_tab,
    send_close_tab,
    send_focus_address_bar,
    send_quick_open,
    send_command_palette,
    type_text,
    press_enter,
)
from tools.workflows import chrome_search
from tools.spotify import (
    spotify_play_pause,
    spotify_next_track,
    spotify_previous_track,
    spotify_volume_up,
    spotify_volume_down,
    spotify_mute,
)

from agent.intents import SUPPORTED_INTENTS


def handle_open_app(command: dict) -> str:
    target = command["target"]

    focus_result = focus_window(target)
    if "not found" not in focus_result.lower():
        return focus_result

    return smart_open(target)


def handle_new_tab(command: dict) -> str:
    send_new_tab()
    return "Opened new tab."


def handle_close_tab(command: dict) -> str:
    send_close_tab()
    return "Closed current tab."


def handle_focus_address_bar(command: dict) -> str:
    send_focus_address_bar()
    return "Focused address bar."


def handle_quick_open(command: dict) -> str:
    send_quick_open()
    return "Opened Quick Open."


def handle_command_palette(command: dict) -> str:
    send_command_palette()
    return "Opened Command Palette."


def handle_type_text(command: dict) -> str:
    text = command["text"]
    type_text(text)
    return f"Typed: {text}"


def handle_press_enter(command: dict) -> str:
    press_enter()
    return "Pressed Enter."


def handle_chrome_new_tab(command: dict) -> str:
    focus_result = focus_window("chrome")
    send_new_tab()
    return f"{focus_result}\nOpened new tab."


def handle_chrome_address_bar(command: dict) -> str:
    focus_result = focus_window("chrome")
    send_focus_address_bar()
    return f"{focus_result}\nFocused address bar."


def handle_vscode_quick_open(command: dict) -> str:
    focus_result = focus_window("code")
    send_quick_open()
    return f"{focus_result}\nOpened Quick Open."


def handle_vscode_command_palette(command: dict) -> str:
    focus_result = focus_window("code")
    send_command_palette()
    return f"{focus_result}\nOpened Command Palette."


HANDLERS = {
    "open_app": handle_open_app,
    "open_by_index": lambda c: open_match_by_index(c["index"]),
    "focus_window": lambda c: focus_window(c["target"]),
    "list_windows": lambda c: list_open_windows(),
    "active_window": lambda c: get_active_window(),
    "new_tab": handle_new_tab,
    "close_tab": handle_close_tab,
    "focus_address_bar": handle_focus_address_bar,
    "quick_open": handle_quick_open,
    "command_palette": handle_command_palette,
    "type_text": handle_type_text,
    "press_enter": handle_press_enter,
    "chrome_new_tab": handle_chrome_new_tab,
    "chrome_address_bar": handle_chrome_address_bar,
    "chrome_search": lambda c: chrome_search(c["query"]),
    "vscode_open_file": lambda c: vscode_open_file(c["filename"]),
    "vscode_search": lambda c: vscode_search(c["query"]),
    "vscode_new_file": lambda c: vscode_new_file(c["filename"]),
    "vscode_quick_open": handle_vscode_quick_open,
    "vscode_command_palette": handle_vscode_command_palette,
    "find_file": lambda c: find_file(c["query"]),
    "create_file": lambda c: create_file(c["name"]),
    "summarize_file": lambda c: summarize_file(c["path"]),
    "save_project": lambda c: save_project_folder(c["path"]),
    "open_last_project": lambda c: open_last_project(),
    "list_projects": lambda c: show_projects(),
    "spotify_play_pause": lambda c: spotify_play_pause(),
    "spotify_next_track": lambda c: spotify_next_track(),
    "spotify_previous_track": lambda c: spotify_previous_track(),
    "spotify_volume_up": lambda c: spotify_volume_up(),
    "spotify_volume_down": lambda c: spotify_volume_down(),
    "spotify_mute": lambda c: spotify_mute(),
}


def execute_command(command: dict) -> str:
    intent = command.get("intent")

    if intent not in SUPPORTED_INTENTS:
        return f"Unsupported intent: {intent}"

    handler = HANDLERS.get(intent)
    if not handler:
        return f"No handler implemented for intent: {intent}"

    try:
        return handler(command)
    except KeyError as e:
        return f"Missing required field for intent '{intent}': {e}"
    except Exception as e:
        return f"Error while executing '{intent}': {e}"