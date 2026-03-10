import time
import keyboard


def send_new_tab():
    time.sleep(0.5)
    keyboard.send("ctrl+t")


def send_close_tab():
    time.sleep(0.5)
    keyboard.send("ctrl+w")


def send_focus_address_bar():
    time.sleep(0.5)
    keyboard.send("ctrl+l")


def send_quick_open():
    time.sleep(0.5)
    keyboard.send("ctrl+p")


def send_command_palette():
    time.sleep(0.5)
    keyboard.send("ctrl+shift+p")


def send_vscode_search():
    time.sleep(0.5)
    keyboard.send("ctrl+shift+f")


def send_vscode_new_file():
    time.sleep(0.5)
    keyboard.send("ctrl+n")


def send_save_as():
    time.sleep(0.5)
    keyboard.send("ctrl+shift+s")


def type_text(text: str):
    time.sleep(0.4)
    keyboard.write(text, delay=0.02)


def press_enter():
    time.sleep(0.3)
    keyboard.send("enter")