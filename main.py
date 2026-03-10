import time
from rich.console import Console

from agent.debug import log_debug
from agent.parser import parse_command
from agent.executor import execute_command
from agent.planner import plan_next_action, warmup_model
from tools.memory import (
    init_db,
    log_command,
    get_workflow,
    save_workflow,
)
from tools.windows import get_active_window

console = Console()

DRY_RUN = True


def get_current_state_summary() -> str:
    try:
        active = get_active_window()
    except Exception as e:
        active = f"Error getting active window: {e}"

    return f"Active window: {active}"


def maybe_cache_workflow(original_input: str, command: dict, source: str):
    intent = command.get("intent")
    if not intent or intent == "done":
        return

    params = {k: v for k, v in command.items() if k != "intent"}
    save_workflow(original_input, intent, params)

    log_debug(
        "workflow_cached",
        {
            "command_text": original_input,
            "intent": intent,
            "params": params,
            "source": source,
        },
    )


def try_cached_workflow(user_input: str) -> bool:
    cached = get_workflow(user_input)

    if not cached:
        return False

    log_debug("workflow_cache_hit", {"user_input": user_input, "cached": cached})
    console.print("[cyan]Jarvis >[/cyan] Using cached workflow")
    console.print(f"[dim]{cached}[/dim]")

    if DRY_RUN:
        console.print("[yellow]Plan Preview:[/yellow]")
        console.print(cached)
        log_debug("plan_preview", {"step": cached, "source": "workflow_cache"})

        confirm = input("Execute? (y/n) ").strip().lower()
        if confirm != "y":
            console.print("[red]Cancelled.[/red]")
            log_debug(
                "plan_cancelled",
                {"step": cached, "source": "workflow_cache"},
            )
            return True

    log_debug("executor_command", {"command": cached, "source": "workflow_cache"})
    result = execute_command(cached)

    log_debug(
        "executor_result",
        {
            "command": cached,
            "result": result,
            "source": "workflow_cache",
        },
    )

    log_command(user_input, cached.get("intent", "unknown"), result)
    console.print(f"[green]Jarvis >[/green] {result}")

    return True


def run_commands(commands, original_input: str):
    for i, command in enumerate(commands):
        log_debug("executor_command", {"command": command, "source": "parser_batch"})

        if DRY_RUN:
            console.print("[yellow]Plan Preview:[/yellow]")
            console.print(command)
            log_debug("plan_preview", {"step": command, "source": "parser_batch"})

            confirm = input("Execute? (y/n) ").strip().lower()
            if confirm != "y":
                console.print("[red]Cancelled.[/red]")
                log_debug(
                    "plan_cancelled",
                    {"step": command, "source": "parser_batch"},
                )
                return

        result = execute_command(command)

        log_debug(
            "executor_result",
            {
                "command": command,
                "result": result,
                "source": "parser_batch",
            },
        )

        log_command(original_input, command.get("intent", "unknown"), result)
        maybe_cache_workflow(original_input, command, "parser_batch")
        console.print(f"[green]Jarvis >[/green] {result}")

        if i < len(commands) - 1:
            time.sleep(0.6)


def run_agent_loop(user_input: str, max_steps: int = 6):
    previous_steps = []
    executed_any = False

    console.print("[cyan]Jarvis >[/cyan] Thinking...")
    log_debug("agent_loop_start", {"user_input": user_input, "max_steps": max_steps})

    for step_number in range(max_steps):
        current_state = get_current_state_summary()

        log_debug(
            "agent_loop_state",
            {
                "step_number": step_number + 1,
                "current_state": current_state,
                "previous_steps": previous_steps,
            },
        )

        next_step = plan_next_action(
            user_goal=user_input,
            current_state=current_state,
            previous_steps=previous_steps,
        )

        log_debug(
            "agent_loop_step",
            {
                "step_number": step_number + 1,
                "next_step": next_step,
            },
        )

        if not next_step or next_step.get("intent") == "done":
            log_debug(
                "agent_loop_stop",
                {
                    "step_number": step_number + 1,
                    "reason": "done_or_empty",
                    "next_step": next_step,
                },
            )
            break

        console.print(f"[dim]Step {step_number + 1}: {next_step}[/dim]")

        if DRY_RUN:
            console.print("[yellow]Plan Preview:[/yellow]")
            console.print(next_step)
            log_debug("plan_preview", {"step": next_step, "source": "agent_loop"})

            confirm = input("Execute? (y/n) ").strip().lower()
            if confirm != "y":
                console.print("[red]Cancelled.[/red]")
                log_debug(
                    "plan_cancelled",
                    {"step": next_step, "source": "agent_loop"},
                )
                return

        log_debug("executor_command", {"command": next_step, "source": "agent_loop"})
        result = execute_command(next_step)
        executed_any = True

        log_debug(
            "executor_result",
            {
                "command": next_step,
                "result": result,
                "source": "agent_loop",
            },
        )

        log_command(user_input, next_step.get("intent", "unknown"), result)
        maybe_cache_workflow(user_input, next_step, "agent_loop")
        console.print(f"[green]Jarvis >[/green] {result}")

        previous_steps.append(next_step)
        time.sleep(0.6)

    if not executed_any:
        console.print("[green]Jarvis >[/green] Sorry, I don't understand that command yet.")
        log_debug(
            "agent_loop_no_execution",
            {
                "user_input": user_input,
                "message": "Sorry, I don't understand that command yet.",
            },
        )


def main():
    init_db()

    console.print("\n[bold cyan]JARVIS - Local Desktop Assistant[/bold cyan]")
    console.print("[dim]Type 'exit' to quit[/dim]\n")

    while True:
        user_input = input("You > ").strip()

        if not user_input:
            continue

        log_debug("user_input", {"input": user_input})

        if user_input.lower() in ["exit", "quit"]:
            console.print("[bold red]Goodbye.[/bold red]")
            log_debug("session_end", {"reason": "user_exit"})
            break

        if try_cached_workflow(user_input):
            continue

        parsed = parse_command(user_input)
        log_debug("parser_output", {"parsed": parsed})

        if isinstance(parsed, list):
            if any(cmd.get("intent") == "unknown" for cmd in parsed):
                log_debug(
                    "parser_fallback_to_planner",
                    {"reason": "unknown_intent_in_list", "parsed": parsed},
                )
                run_agent_loop(user_input)
            else:
                run_commands(parsed, user_input)
            continue

        if parsed.get("intent") == "unknown":
            log_debug(
                "parser_fallback_to_planner",
                {"reason": "unknown_single_intent", "parsed": parsed},
            )
            run_agent_loop(user_input)
            continue

        log_debug("executor_command", {"command": parsed, "source": "parser_single"})

        if DRY_RUN:
            console.print("[yellow]Plan Preview:[/yellow]")
            console.print(parsed)
            log_debug("plan_preview", {"step": parsed, "source": "parser_single"})

            confirm = input("Execute? (y/n) ").strip().lower()
            if confirm != "y":
                console.print("[red]Cancelled.[/red]")
                log_debug(
                    "plan_cancelled",
                    {"step": parsed, "source": "parser_single"},
                )
                continue

        result = execute_command(parsed)

        log_debug(
            "executor_result",
            {
                "command": parsed,
                "result": result,
                "source": "parser_single",
            },
        )

        log_command(user_input, parsed.get("intent", "unknown"), result)
        maybe_cache_workflow(user_input, parsed, "parser_single")
        console.print(f"[green]Jarvis >[/green] {result}")


if __name__ == "__main__":
    warmup_model()
    main()