import time
import keyboard


def send_new_tab() -> str:
    time.sleep(0.6)
    keyboard.send("ctrl+t")
    return "Opened new tab."


def send_close_tab() -> str:
    time.sleep(0.6)
    keyboard.send("ctrl+w")
    return "Closed current tab."


def send_focus_address_bar() -> str:
    time.sleep(0.6)
    keyboard.send("ctrl+l")
    return "Focused address bar."


def send_quick_open() -> str:
    time.sleep(0.6)
    keyboard.send("ctrl+p")
    return "Opened Quick Open."


def send_command_palette() -> str:
    time.sleep(0.6)
    keyboard.send("ctrl+shift+p")
    return "Opened Command Palette."