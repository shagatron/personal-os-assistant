import time

from tools.windows import focus_window
from tools.shortcuts import (
    send_quick_open,
    send_vscode_search,
    send_vscode_new_file,
    send_save_as,
    type_text,
    press_enter,
)


def vscode_open_file(filename: str) -> str:
    focus_result = focus_window("code")

    time.sleep(0.6)

    send_quick_open()
    type_text(filename)
    press_enter()

    return f"{focus_result}\nOpening file in VS Code: {filename}"


def vscode_search(query: str) -> str:
    focus_result = focus_window("code")

    time.sleep(0.6)

    send_vscode_search()
    type_text(query)

    return f"{focus_result}\nSearching in VS Code: {query}"


def vscode_new_file(filename: str) -> str:
    focus_result = focus_window("code")

    time.sleep(0.6)

    send_vscode_new_file()
    time.sleep(0.4)
    send_save_as()
    type_text(filename)
    press_enter()

    return f"{focus_result}\nCreating new file in VS Code: {filename}"