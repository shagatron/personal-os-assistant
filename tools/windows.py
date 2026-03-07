import win32gui
import win32con
import win32com.client


def focus_window(window_name: str) -> str:
    window_name = window_name.lower()

    def enum_handler(hwnd, windows):
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd).strip()
        if not title:
            return

        if window_name in title.lower():
            windows.append((hwnd, title))

    matches = []
    win32gui.EnumWindows(enum_handler, matches)

    if not matches:
        return f"No open window found matching '{window_name}'."

    hwnd, title = matches[0]

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys("%")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return f"Focused window: {title}"
    except Exception as e:
        return f"Failed to focus window '{title}': {e}"


def list_open_windows() -> str:
    windows = []
    seen_titles = set()

    def enum_handler(hwnd, results):
        if not win32gui.IsWindowVisible(hwnd):
            return

        if win32gui.GetParent(hwnd) != 0:
            return

        title = win32gui.GetWindowText(hwnd).strip()
        if not title:
            return

        if title in seen_titles:
            return

        exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if exstyle & win32con.WS_EX_TOOLWINDOW:
            return

        seen_titles.add(title)
        results.append(title)

    win32gui.EnumWindows(enum_handler, windows)

    if not windows:
        return "No open windows found."

    lines = [f"{i + 1}. {title}" for i, title in enumerate(windows[:20])]
    return "Open windows:\n" + "\n".join(lines)


def get_active_window() -> str:
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd).strip()

        if not title:
            return "No active window detected."

        return f"Active window: {title}"
    except Exception as e:
        return f"Failed to get active window: {e}"