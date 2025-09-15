import argparse
import subprocess
import json
import os
import sys
from datetime import datetime, timezone

SESSION_LOG_FILE = '.session_actions.json'

def main():
    parser = argparse.ArgumentParser(description="Execute a command and log it with intent.")
    parser.add_argument('--reason', required=True, help="The reason for running this command.")
    parser.add_argument('--decision', required=True, help="The decision-making process behind this command.")
    parser.add_argument('--command', required=True, help="The shell command to execute.")
    args = parser.parse_args()

    result = subprocess.run(args.command, shell=True, capture_output=True, text=True)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason": args.reason,
        "decision": args.decision,
        "command": args.command,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "returncode": result.returncode
    }

    logs = []
    if os.path.exists(SESSION_LOG_FILE):
        with open(SESSION_LOG_FILE, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
                print("WARNING: Corrupt session log. Overwriting.")

    logs.append(log_entry)

    with open(SESSION_LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

    print(result.stdout)
    if result.stderr:
        print("\nSTDERR: ", file=sys.stderr)
        print(result.stderr, file=sys.stderr)

if __name__ == "__main__":
    main()
