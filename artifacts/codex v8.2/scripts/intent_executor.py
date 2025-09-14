# scripts/intent_executor.py

import argparse
import subprocess
import json
import os
from datetime import datetime

SESSION_LOG_FILE = '.session_actions.json'

def main():
    """
    Executes a command and logs it with the agent's provided intent.
    This is the primary tool for all state-changing actions.
    """
    parser = argparse.ArgumentParser(
        description="Execute a command and log it with intent."
    )
    parser.add_argument(
        '--reason',
        required=True,
        help="The reason for running this command."
    )
    parser.add_argument(
        '--decision',
        required=True,
        help="The decision-making process behind this command."
    )
    parser.add_argument(
        '--command',
        required=True,
        help="The shell command to execute."
    )
    args = parser.parse_args()

    # Execute the command
    print(f"Executing command: {args.command}")
    result = subprocess.run(
        args.command,
        shell=True,
        capture_output=True,
        text=True
    )

    # Prepare the log entry
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'reason': args.reason,
        'decision': args.decision,
        'command': args.command,
        'stdout': result.stdout.strip(),
        'stderr': result.stderr.strip(),
        'returncode': result.returncode
    }

    # Load existing logs and append the new entry
    if os.path.exists(SESSION_LOG_FILE):
        with open(SESSION_LOG_FILE, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    logs.append(log_entry)

    # Write back to the session log
    with open(SESSION_LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

    # Output results to the agent's console
    print("\n--- STDOUT ---")
    print(result.stdout)
    print("--- STDERR ---")
    print(result.stderr)
    print(f"\nAction logged successfully. Exit Code: {result.returncode}")

if __name__ == "__main__":
    main()