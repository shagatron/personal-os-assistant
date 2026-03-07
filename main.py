import time

from agent.parser import parse_command
from agent.executor import execute_command
from tools.memory import init_db, log_command


def main():
    init_db()
    print("Personal OS Assistant started. Type 'exit' to quit.\n")

    while True:
        user_input = input(">>> ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye.")
            break

        parsed = parse_command(user_input)

        if isinstance(parsed, list):
            results = []

            for i, command in enumerate(parsed):
                result = execute_command(command)
                results.append(result)

                log_command(user_input, command.get("intent", "unknown"), result)

                # small delay between chained actions
                if i < len(parsed) - 1:
                    time.sleep(0.6)

            print("\n".join(results))
        else:
            result = execute_command(parsed)
            log_command(user_input, parsed.get("intent", "unknown"), result)
            print(result)


if __name__ == "__main__":
    main()