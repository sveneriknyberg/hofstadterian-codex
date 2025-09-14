# scripts/consolidate_handoff.py

import json
import os
from datetime import datetime

SESSION_LOG_FILE = '.session_actions.json'
ARTIFACTS_DIR = 'artifacts'
HANDOFFS_DIR = 'handoffs'
WISDOM_PACKET_PREFIX = 'wisdom_packet_'

def find_latest_wisdom_packet():
    """Finds the most recent wisdom packet in the artifacts directory."""
    if not os.path.exists(ARTIFACTS_DIR):
        os.makedirs(ARTIFACTS_DIR)
        return None

    packets = [f for f in os.listdir(ARTIFACTS_DIR) if f.startswith(WISDOM_PACKET_PREFIX)]
    if not packets:
        return None

    return max(packets, key=lambda f: os.path.getmtime(os.path.join(ARTIFACTS_DIR, f)))

def main():
    """
    Consolidates session actions into a new wisdom packet and generates a handoff summary.
    """
    if not os.path.exists(SESSION_LOG_FILE):
        print("Error: No session log file (.session_actions.json) found. Nothing to consolidate.")
        return

    with open(SESSION_LOG_FILE, 'r') as f:
        try:
            session_actions = json.load(f)
            if not session_actions:
                print("Warning: Session log is empty. No new handoff will be created.")
                return
        except json.JSONDecodeError:
            print("Error: Session log is corrupted. Cannot consolidate.")
            return

    # Load the previous wisdom packet or create a new one
    latest_packet_file = find_latest_wisdom_packet()
    if latest_packet_file:
        with open(os.path.join(ARTIFACTS_DIR, latest_packet_file), 'r') as f:
            wisdom = json.load(f)
    else:
        wisdom = {'version': 0, 'history': []}

    # Update the wisdom packet
    wisdom['version'] += 1
    session_summary = {
        'session_id': wisdom['version'],
        'timestamp': datetime.utcnow().isoformat(),
        'actions': session_actions
    }
    wisdom['history'].append(session_summary)
    
    # Create directories if they don't exist
    os.makedirs(HANDOFFS_DIR, exist_ok=True)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    # Save the new wisdom packet
    timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    new_packet_filename = os.path.join(ARTIFACTS_DIR, f"{WISDOM_PACKET_PREFIX}{timestamp_str}.json")
    with open(new_packet_filename, 'w') as f:
        json.dump(wisdom, f, indent=2)
    print(f"Successfully created new wisdom packet: {new_packet_filename}")

    # Generate human-readable handoff
    handoff_content = f"# Handoff for Session {wisdom['version']} - {timestamp_str}\n\n"
    handoff_content += "## Summary of Actions\n\n"
    for i, action in enumerate(session_actions, 1):
        handoff_content += f"### Action {i}\n\n"
        handoff_content += f"**Reason:** {action['reason']}\n\n"
        handoff_content += f"**Decision:** {action['decision']}\n\n"
        handoff_content += f"**Command:**\n```bash\n{action['command']}\n```\n\n"
        handoff_content += f"**Result (Exit Code {action['returncode']}):**\n"
        if action['stdout']:
            handoff_content += f"**STDOUT:**\n```\n{action['stdout']}\n```\n"
        if action['stderr']:
            handoff_content += f"**STDERR:**\n```\n{action['stderr']}\n```\n"
        handoff_content += "---\n"

    handoff_filename = os.path.join(HANDOFFS_DIR, f"{timestamp_str}.md")
    with open(handoff_filename, 'w') as f:
        f.write(handoff_content)
    print(f"Successfully generated human-readable handoff: {handoff_filename}")

    # Archive the session log
    os.rename(SESSION_LOG_FILE, f"{SESSION_LOG_FILE}.{timestamp_str}.bak")
    print(f"Archived session log. The system is ready for the next session.")

if __name__ == "__main__":
    main()