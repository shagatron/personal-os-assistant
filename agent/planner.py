import json
import os
from typing import Any, Dict, List

import requests

from agent.debug import log_debug
from agent.intents import INTENT_DESCRIPTIONS, REQUIRED_FIELDS, SUPPORTED_INTENTS


PLANNER_INTENTS = SUPPORTED_INTENTS + ["done"]


def build_intent_docs() -> str:
    lines = []
    for intent in SUPPORTED_INTENTS:
        desc = INTENT_DESCRIPTIONS.get(intent, "")
        required = REQUIRED_FIELDS.get(intent, [])
        required_text = f" Required fields: {required}." if required else ""
        lines.append(f"- {intent}: {desc}{required_text}")
    return "\n".join(lines)


SYSTEM_PROMPT = f"""
You are JARVIS, an AI planner for a local desktop assistant.

Your job is to choose the SINGLE BEST next action for the user's goal.

You must return exactly one JSON object.

Available intents:
{build_intent_docs()}

Rules:
- Return ONLY valid JSON
- Do not explain anything
- Do not use markdown
- Do not return a JSON array
- Only use these intents: {PLANNER_INTENTS}
- If the task is already complete, return: {{"intent": "done"}}
- Prefer the smallest useful next action
- Prefer high-level workflow intents when available
- Prefer focus_window when the user wants to switch to an already open app
- Prefer open_app only when the app likely needs to be launched
- Never invent new intents or fields

Examples:

User goal: pause spotify
Output:
{{"intent": "spotify_play_pause"}}

User goal: play the next song
Output:
{{"intent": "spotify_next_track"}}

User goal: go to previous track on spotify
Output:
{{"intent": "spotify_previous_track"}}

User goal: increase volume
Output:
{{"intent": "spotify_volume_up"}}

User goal: search github in chrome
Output:
{{"intent": "chrome_search", "query": "github"}}

User goal: switch to chrome
Output:
{{"intent": "focus_window", "target": "chrome"}}

User goal: open chrome
Output:
{{"intent": "open_app", "target": "chrome"}}

User goal: open my last project
Output:
{{"intent": "open_last_project"}}

User goal: create a file called ideas.txt
Output:
{{"intent": "create_file", "name": "ideas.txt"}}

User goal: the task is complete
Output:
{{"intent": "done"}}
""".strip()


def warmup_model() -> None:
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    try:
        requests.post(
            f"{host}/api/generate",
            json={
                "model": model,
                "prompt": "",
                "keep_alive": "30m",
                "stream": False,
            },
            timeout=20,
        )
        print("[Planner] Ollama model warmed up.")
        log_debug("planner_warmup", {"status": "success", "model": model, "host": host})
    except Exception as e:
        print(f"[Planner Warmup Warning] {e}")
        log_debug(
            "planner_warmup",
            {"status": "error", "model": model, "host": host, "error": str(e)},
        )


def call_llm(prompt: str) -> str:
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    payload = {
        "model": model,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "format": "json",
        "keep_alive": "30m",
        "options": {
            "temperature": 0,
        },
    }

    try:
        response = requests.post(
            f"{host}/api/generate",
            json=payload,
            timeout=25,
        )
        response.raise_for_status()
        data = response.json()

        total_s = data.get("total_duration", 0) / 1_000_000_000
        load_s = data.get("load_duration", 0) / 1_000_000_000

        print(f"[Planner Timing] total={total_s:.2f}s load={load_s:.2f}s")
        log_debug(
            "planner_timing",
            {
                "model": model,
                "host": host,
                "total_seconds": total_s,
                "load_seconds": load_s,
            },
        )

        return data.get("response", "{}")

    except requests.exceptions.Timeout:
        print("[Planner Error] Ollama request timed out.")
        log_debug(
            "planner_call_error",
            {"type": "timeout", "model": model, "host": host},
        )
        return '{"intent": "done"}'

    except requests.exceptions.ConnectionError:
        print("[Planner Error] Could not connect to Ollama. Is it running?")
        log_debug(
            "planner_call_error",
            {"type": "connection_error", "model": model, "host": host},
        )
        return '{"intent": "done"}'

    except Exception as e:
        print(f"[Planner Error] {e}")
        log_debug(
            "planner_call_error",
            {"type": "exception", "model": model, "host": host, "error": str(e)},
        )
        return '{"intent": "done"}'


def is_valid_step(step: Dict[str, Any]) -> bool:
    intent = step.get("intent")

    if intent not in PLANNER_INTENTS:
        return False

    if intent == "done":
        return True

    required_fields = REQUIRED_FIELDS.get(intent, [])
    for field in required_fields:
        if field not in step:
            return False

    if intent == "open_by_index" and not isinstance(step.get("index"), int):
        return False

    return True


def validate_step(step: Any) -> Dict[str, Any]:
    if not isinstance(step, dict):
        return {"intent": "done"}

    if not is_valid_step(step):
        return {"intent": "done"}

    return step


def build_planner_prompt(
    user_goal: str,
    current_state: str,
    previous_steps: List[Dict[str, Any]],
) -> str:
    return f"""
User goal:
{user_goal}

Current desktop state:
{current_state}

Previous steps already executed:
{json.dumps(previous_steps, indent=2)}

Choose the single best next action.

Return exactly one JSON object.
""".strip()


def plan_next_action(
    user_goal: str,
    current_state: str,
    previous_steps: List[Dict[str, Any]],
) -> Dict[str, Any]:
    prompt = build_planner_prompt(
        user_goal=user_goal,
        current_state=current_state,
        previous_steps=previous_steps,
    )

    log_debug(
        "planner_prompt",
        {
            "user_goal": user_goal,
            "current_state": current_state,
            "previous_steps": previous_steps,
            "prompt": prompt,
        },
    )

    raw = call_llm(prompt).strip()
    print("[Raw Planner Output]", raw)

    log_debug("planner_raw_output", {"raw": raw})

    if not raw:
        log_debug("planner_empty_output", {"fallback": {"intent": "done"}})
        return {"intent": "done"}

    try:
        parsed = json.loads(raw)
        validated = validate_step(parsed)

        log_debug(
            "planner_validated_step",
            {
                "parsed": parsed,
                "validated": validated,
            },
        )

        return validated

    except json.JSONDecodeError:
        print(f"[Planner Error] Model returned invalid JSON: {raw}")
        log_debug("planner_json_error", {"raw": raw})
        return {"intent": "done"}