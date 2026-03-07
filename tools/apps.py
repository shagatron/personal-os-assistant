import subprocess

KNOWN_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "explorer": "explorer.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode": r"C:\Users\Aaditya Shah\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "spotify": r"C:\Users\Aaditya Shah\AppData\Roaming\Spotify\Spotify.exe",
}


def search_apps(query: str):
    query = query.lower().strip()
    matches = []

    for app_name in KNOWN_APPS:
        if query in app_name.lower():
            matches.append({
                "type": "app",
                "name": app_name,
                "value": app_name
            })

    return matches


def open_app(app_name: str):
    app_name = app_name.lower().strip()

    if app_name not in KNOWN_APPS:
        return None

    try:
        subprocess.Popen(KNOWN_APPS[app_name])
        return f"Opened app: {app_name}"
    except Exception as e:
        return f"Failed to open app '{app_name}': {e}"