import argparse
import subprocess
import sys
import shlex
import json

def get_read_only_commands():
    with open('config/read_only_commands.json', 'r') as f:
        return json.load(f)

def is_state_changing(command_list):
    if not command_list:
        return False
    first_word = command_list[0]
    if first_word == 'bash' and len(command_list) > 1 and "preflight_check.sh" in command_list[1]:
        return False
    if first_word == 'python3' and len(command_list) > 1 and "intent_executor.py" in command_list[1]:
        return False
    READ_ONLY_COMMANDS = get_read_only_commands()
    return first_word not in READ_ONLY_COMMANDS

def main():
    parser = argparse.ArgumentParser(description="A protocol-enforcing shell for the agent.")
    parser.add_argument('command', nargs=argparse.REMAINDER, help="The command to execute.")
    args = parser.parse_args()

    full_command_list = args.command
    full_command_str = shlex.join(full_command_list)

    if not full_command_str:
        print("ERROR: No command provided.", file=sys.stderr)
        sys.exit(1)

    if is_state_changing(full_command_list):
        print("--- PROTOCOL VIOLATION DETECTED ---", file=sys.stderr)
        print(f"ERROR: The command '{full_command_str}' is a state-changing operation.", file=sys.stderr)
        print("You MUST use 'scripts/intent_executor.py' to perform this action.", file=sys.stderr)
        sys.exit(1)
    else:
        subprocess.run(full_command_str, shell=True, text=True)

if __name__ == "__main__":
    main()
