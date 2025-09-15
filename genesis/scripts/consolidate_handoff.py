# scripts/consolidate_handoff.py

import hashlib
import json
import os
from datetime import datetime

# --- Configuration ---
SESSION_LOG_FILE = '.session_actions.json'
ARTIFACTS_DIR = 'artifacts'
HANDOFFS_DIR = 'handoffs'
ARCHIVE_DIR = 'artifacts/archive'
WISDOM_PACKET_PREFIX = 'wisdom_packet_'
MAX_HISTORY_SIZE = 50

def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def find_latest_wisdom_packet():
    if not os.path.exists(ARTIFACTS_DIR): return None
    packets = [f for f in os.listdir(ARTIFACTS_DIR) if f.startswith(WISDOM_PACKET_PREFIX)]
    if not packets: return None
    return max(packets, key=lambda f: os.path.getmtime(os.path.join(ARTIFACTS_DIR, f)))

def main():
    if not os.path.exists(SESSION_LOG_FILE):
        print("Error: No session log found.")
        return

    with open(SESSION_LOG_FILE, 'r') as f:
        try:
            session_actions = json.load(f)
            if not session_actions:
                print("Warning: Session log is empty.")
                return
        except json.JSONDecodeError:
            print("Error: Session log is corrupted.")
            return

    latest_packet_file = find_latest_wisdom_packet()
    if latest_packet_file:
        with open(os.path.join(ARTIFACTS_DIR, latest_packet_file), 'r') as f:
            wisdom = json.load(f)

        if len(wisdom.get('history', [])) >= MAX_HISTORY_SIZE:
            print(f"⚠️  Wisdom Packet history limit ({MAX_HISTORY_SIZE}) reached. Rotating...")
            os.makedirs(ARCHIVE_DIR, exist_ok=True)
            archive_path = os.path.join(ARCHIVE_DIR, os.path.basename(latest_packet_file))
            os.rename(os.path.join(ARTIFACTS_DIR, latest_packet_file), archive_path)

            summary_entry = {"session_id": 0, "timestamp": datetime.utcnow().isoformat(), "actions": [{"event": "ROTATION", "details": f"History archived in {archive_path}"}]}
            wisdom = {'version': 0, 'history': [summary_entry]}
    else:
        wisdom = {'version': 0, 'history': []}

    wisdom['version'] += 1
    session_summary = {'session_id': wisdom['version'], 'timestamp': datetime.utcnow().isoformat(), 'actions': session_actions}
    wisdom['history'].append(session_summary)

    timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    new_packet_filename = os.path.join(ARTIFACTS_DIR, f"{WISDOM_PACKET_PREFIX}{timestamp_str}.json")
    with open(new_packet_filename, 'w') as f:
        json.dump(wisdom, f, indent=2)

    packet_hash = calculate_sha256(new_packet_filename)
    print(f"Successfully created new wisdom packet with SHA256: {packet_hash}")

    handoff_content = f"# Handoff for Session {wisdom['version']} - {timestamp_str}\n\n## Summary of Actions\n\n"
    for i, action in enumerate(session_actions, 1):
        handoff_content += f"### Action {i}\n\n**Reason:** {action['reason']}\n\n**Decision:** {action['decision']}\n\n"
        handoff_content += f"**Command:**\n```bash\n{action['command']}\n```\n\n**Result (Exit Code {action['returncode']}):**\n"
        if action['stdout']: handoff_content += f"**STDOUT:**\n```\n{action['stdout']}\n```\n"
        if action['stderr']: handoff_content += f"**STDERR:**\n```\n{action['stderr']}\n```\n"
        handoff_content += "---\n"

    handoff_content += f"\n## Verification\n\n**Wisdom Packet SHA256:** `{packet_hash}`\n"

    handoff_filename = os.path.join(HANDOFFS_DIR, f"{timestamp_str}.md")
    with open(handoff_filename, 'w') as f:
        f.write(handoff_content)
    print(f"Successfully generated human-readable handoff: {handoff_filename}")

    os.rename(SESSION_LOG_FILE, f"{SESSION_LOG_FILE}.{timestamp_str}.bak")
    print(f"Archived session log. The system is ready for the next session.")

if __name__ == "__main__":
    main()
