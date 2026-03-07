from agent.parser import parse_command
from agent.executor import execute_command


def main():
    print("Personal OS Assistant started. Type 'exit' to quit.\n")

    while True:
        user_input = input(">>> ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye.")
            break

        command = parse_command(user_input)
        result = execute_command(command)

        print(result)


if __name__ == "__main__":
    main()