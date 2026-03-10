import json
import time
from pathlib import Path


LOG_FILE = Path("jarvis_debug.log")


def log_debug(event: str, data: dict) -> None:
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "data": data,
    }

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")