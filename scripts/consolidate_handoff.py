# scripts/consolidate_handoff.py
import json
import os
import sys
from datetime import datetime, timezone

SESSION_LOG_FILE = '.session_actions.json'
ARTIFACTS_DIR = 'artifacts'
WISDOM_PACKET_PREFIX = 'wisdom_packet_'

def main():
    if not os.path.exists(SESSION_LOG_FILE):
        print("ERROR: No session log found. Cannot consolidate handoff.")
        sys.exit(1)

    with open(SESSION_LOG_FILE, 'r') as f:
        try:
            session_actions = json.load(f)
        except json.JSONDecodeError:
            print("ERROR: Session log is corrupted.")
            sys.exit(1)

    if not session_actions:
        print("WARNING: Session log is empty. No wisdom packet created.")
        return

    timestamp_str = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    new_packet_filename = os.path.join(ARTIFACTS_DIR, f"{WISDOM_PACKET_PREFIX}{timestamp_str}.json")

    if not os.path.exists(ARTIFACTS_DIR):
        os.makedirs(ARTIFACTS_DIR)

    with open(new_packet_filename, 'w') as f:
        json.dump(session_actions, f, indent=2)

    print(f"Successfully created wisdom packet: {new_packet_filename}")

if __name__ == "__main__":
    main()
