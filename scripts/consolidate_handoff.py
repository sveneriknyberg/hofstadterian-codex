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
        print("Error: No session log found. Run intent_executor.py to create actions.")
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
    else:
        # Create a new wisdom packet from scratch if none exists
        wisdom = {
            "metadata": {"wisdom_packet_version": "2.0", "total_sessions": 0},
            "session_summaries": [], "analogies": {}, "proven_workflows": [],
            "session_history": [], "semantic_insights": []
        }

    # Use the new schema
    current_session_count = wisdom.get("metadata", {}).get("total_sessions", 0)
    new_session_count = current_session_count + 1
    wisdom["metadata"]["total_sessions"] = new_session_count
    wisdom["metadata"]["last_updated"] = datetime.utcnow().isoformat()

    # Add the current session actions to the history
    session_summary = {
        "session_id": new_session_count,
        "timestamp": datetime.utcnow().isoformat(),
        "actions": session_actions
    }
    wisdom.get("session_history", []).append(session_summary)

    # Create a simple summary for the handoff
    summary_text = f"Session {new_session_count}: Executed {len(session_actions)} actions."
    key_decisions = [action['decision'] for action in session_actions]
    
    wisdom.get("session_summaries", []).append({
        "timestamp": datetime.utcnow().isoformat(),
        "summary_text": summary_text,
        "key_decisions": key_decisions,
        "lessons_learned": ["LESSON: Retroactively reconstructed session log to adhere to protocol."]
    })

    timestamp_str = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S')
    new_packet_filename = os.path.join(ARTIFACTS_DIR, f"{WISDOM_PACKET_PREFIX}{timestamp_str}.json")
    with open(new_packet_filename, 'w') as f:
        json.dump(wisdom, f, indent=2)

    packet_hash = calculate_sha256(new_packet_filename)
    print(f"Successfully created new wisdom packet with SHA256: {packet_hash}")
    
    # Create a more structured handoff file
    handoff_content = f"# Handoff for Session {new_session_count} - {timestamp_str}\n\n"
    handoff_content += f"## 1. Summary of Work\n\n{summary_text}\n\n"
    handoff_content += "## 2. Key Decisions\n\n"
    for decision in key_decisions:
        handoff_content += f"- {decision}\n"

    handoff_content += "\n## 3. Raw Actions Log\n\n"
    for i, action in enumerate(session_actions, 1):
        handoff_content += f"### Action {i}\n\n**Reason:** {action['reason']}\n\n**Decision:** {action['decision']}\n\n"
        handoff_content += f"**Command:**\n```bash\n{action['command']}\n```\n\n"
        if action['stdout']: handoff_content += f"**STDOUT:**\n```\n{action['stdout']}\n```\n"
        if action['stderr']: handoff_content += f"**STDERR:**\n```\n{action['stderr']}\n```\n"
        handoff_content += "---\n"
    
    handoff_content += f"\n## Verification\n\n**Wisdom Packet SHA256:** `{packet_hash}`\n"
    
    os.makedirs(HANDOFFS_DIR, exist_ok=True)
    handoff_filename = os.path.join(HANDOFFS_DIR, f"{timestamp_str}.md")
    with open(handoff_filename, 'w') as f:
        f.write(handoff_content)
    print(f"Successfully generated human-readable handoff: {handoff_filename}")

    # Archive the session log
    archive_log_filename = f"{SESSION_LOG_FILE}.{timestamp_str}.bak"
    os.rename(SESSION_LOG_FILE, os.path.join(ARTIFACTS_DIR, archive_log_filename))
    print(f"Archived session log to {os.path.join(ARTIFACTS_DIR, archive_log_filename)}. The system is ready for the next session.")

if __name__ == "__main__":
    main()