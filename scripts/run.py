# scripts/run.py
# The v14.2 Unified Command Gateway

import subprocess
import argparse
import json
import os
import sys
import base64
from datetime import datetime, timezone

SESSION_LOG_FILE = 'session.log'

def log_action(log_entry):
    with open(SESSION_LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def main():
    parser = argparse.ArgumentParser(description="v14.2 Unified Command Gateway: Logs intent and executes a command.")
    parser.add_argument("--intent", required=True, help="The agent's intent for this action.")
    parser.add_argument("--command", required=True, help="The command to execute.")
    args = parser.parse_args()

    log_action({
        "type": "intent",
        "details": args.intent,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    command_to_run = args.command
    
    if "consolidate_handoff.py" in command_to_run:
        if os.path.exists(SESSION_LOG_FILE):
            with open(SESSION_LOG_FILE, 'rb') as f:
                session_data_b64 = base64.b64encode(f.read()).decode('utf-8')
            command_to_run += f" --session-data '{session_data_b64}'"

    try:
        result = subprocess.run(command_to_run, shell=True, check=True, capture_output=True, text=True, executable='/bin/bash')
        stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        stdout, stderr, returncode = e.stdout, e.stderr, e.returncode
    
    log_action({
        "type": "command_result",
        "command": args.command,
        "returncode": returncode,
        "stdout": stdout.strip(),
        "stderr": stderr.strip(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
        
    sys.exit(returncode)

if __name__ == "__main__":
    main()