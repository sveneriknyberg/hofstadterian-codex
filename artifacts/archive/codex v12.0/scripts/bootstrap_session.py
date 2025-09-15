# scripts/bootstrap_session.py

import os
import json
import sys
import subprocess

def find_latest_wisdom_packet():
    """Finds the most recent wisdom packet."""
    artifacts_dir = 'artifacts'
    if not os.path.exists(artifacts_dir): return None
    packets = [f for f in os.listdir(artifacts_dir) if f.startswith('wisdom_packet_')]
    if not packets: return None
    return max(packets, key=lambda f: os.path.getmtime(os.path.join(artifacts_dir, f)))

def main():
    """Runs a pre-flight check, then prepares the session and prompts the user."""
    
    # 1. Run the pre-flight check first for safety and validation.
    try:
        result = subprocess.run(
            "bash preflight_check.sh",
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        failure_briefing = {
            "status": "SESSION_FAILED_TO_START",
            "message": "The pre-flight check failed. Environment is not safe.",
            "details": e.stderr.strip()
        }
        print(json.dumps(failure_briefing, indent=2))
        sys.exit(1)

    # 2. Find context and formulate the briefing.
    latest_packet = find_latest_wisdom_packet()
    context_message = f"Latest context found in: {latest_packet}" if latest_packet else "No prior context found."
    
    briefing = {
        "status": "SESSION_STARTED",
        "message": "Hofstadterian Protocol v12.0 session is active. All rules in AGENTS.md are in effect.",
        "context": context_message,
        "next_step": {
            "status": "HUMAN_INPUT_REQUIRED",
            "prompt": "Please state your high-level objective."
        }
    }

    print(json.dumps(briefing, indent=2))

if __name__ == "__main__":
    main()