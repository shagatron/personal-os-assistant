import os
import asyncio
import discord
from discord import app_commands
from dotenv import load_dotenv

from agent.parser import parse_command
from agent.executor import execute_command
from agent.planner import plan_next_action
from tools.memory import init_db, log_command
from tools.windows import get_active_window, list_open_windows

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def get_current_state_summary():
    try:
        active = get_active_window()
    except Exception as e:
        active = f"Error: {e}"

    try:
        windows = list_open_windows()
    except Exception as e:
        windows = f"Error: {e}"

    return f"Active window: {active}\nOpen windows: {windows}"


def run_agent_loop_sync(user_input: str, max_steps: int = 6):
    previous_steps = []
    outputs = []

    for _ in range(max_steps):
        state = get_current_state_summary()

        step = plan_next_action(
            user_goal=user_input,
            current_state=state,
            previous_steps=previous_steps,
        )

        if not step or step.get("intent") == "done":
            break

        result = execute_command(step)
        outputs.append(f"{step} -> {result}")

        log_command(user_input, step.get("intent", "unknown"), result)
        previous_steps.append(step)

    return outputs


@client.event
async def on_ready():
    init_db()

    await tree.sync()   # global command sync

    print(f"Logged in as {client.user}")


@tree.command(name="jarvis", description="Send a command to JARVIS")
@app_commands.describe(command="Command for JARVIS")
async def jarvis(interaction: discord.Interaction, command: str):

    await interaction.response.defer(thinking=True)

    def handle():
        parsed = parse_command(command)

        if isinstance(parsed, list):

            if any(cmd.get("intent") == "unknown" for cmd in parsed):
                outputs = run_agent_loop_sync(command)
                return "\n".join(outputs) if outputs else "I couldn't understand that."

            results = []
            for cmd in parsed:
                result = execute_command(cmd)
                results.append(result)
                log_command(command, cmd.get("intent", "unknown"), result)

            return "\n".join(results)

        if parsed.get("intent") == "unknown":
            outputs = run_agent_loop_sync(command)
            return "\n".join(outputs) if outputs else "I couldn't understand that."

        result = execute_command(parsed)
        log_command(command, parsed.get("intent", "unknown"), result)

        return result

    result = await asyncio.to_thread(handle)

    await interaction.followup.send(f"**Command:** {command}\n{result}")


client.run(TOKEN)