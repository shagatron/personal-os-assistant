import time

from tools.windows import focus_window
from tools.shortcuts import (
    send_new_tab,
    send_focus_address_bar,
    type_text,
    press_enter,
)


def chrome_search(query: str) -> str:
    focus_result = focus_window("chrome")

    time.sleep(0.6)

    send_new_tab()
    send_focus_address_bar()
    type_text(query)
    press_enter()

    return f"{focus_result}\nSearching Chrome for: {query}"