import json
import os
import glob
from datetime import datetime

# --- Configuration ---
WISDOM_PACKET_DIR = "artifacts"
HANDOFF_DIR = "handoffs"
SESSION_HISTORY_FILE = ".session_history.json"
ANALOGIES_REGISTRY_FILE = "analogies/registry.json"
CONTEXT_DIR = "context"

# Input files for the non-interactive process
INPUT_SUMMARY_FILE = os.path.join(CONTEXT_DIR, "handoff_summary.txt")
INPUT_DECISIONS_FILE = os.path.join(CONTEXT_DIR, "handoff_decisions.log")
INPUT_LESSONS_FILE = os.path.join(CONTEXT_DIR, "handoff_lessons.log")

# --- Helper functions for file operations ---

def read_file_lines(filepath):
    """Reads a file and returns a list of non-empty lines."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def read_file_content(filepath):
    """Reads the entire content of a file."""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, 'r') as f:
        return f.read().strip()

def load_json(filepath):
    """Loads a JSON file."""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON file '{filepath}'.")
            return None

def find_latest_wisdom_packet():
    """Finds the most recent wisdom packet in the artifacts directory."""
    list_of_files = glob.glob(os.path.join(WISDOM_PACKET_DIR, 'wisdom_packet_*.json'))
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

# --- Main Logic ---
def main():
    print("--- Starting Automated Handoff Consolidation Process ---")

    # 1. Load the latest wisdom packet, or create a new one
    latest_packet_path = find_latest_wisdom_packet()
    if latest_packet_path:
        print(f"Loading previous wisdom from: {latest_packet_path}")
        wisdom_packet = load_json(latest_packet_path)
        if wisdom_packet is None:
            print("Error: Could not load latest wisdom packet. Starting fresh.")
            wisdom_packet = {}
    else:
        print("No previous wisdom packet found. Creating a new one.")
        wisdom_packet = {}

    # 2. Initialize sections if they don't exist
    wisdom_packet.setdefault("metadata", {"wisdom_packet_version": "2.0"})
    wisdom_packet.setdefault("session_summaries", [])
    wisdom_packet.setdefault("analogies", {})
    wisdom_packet.setdefault("proven_workflows", [])
    wisdom_packet.setdefault("session_history", [])

    # 3. Load new session data from files
    summary = read_file_content(INPUT_SUMMARY_FILE)
    decisions = read_file_lines(INPUT_DECISIONS_FILE)
    lessons = read_file_lines(INPUT_LESSONS_FILE)

    if not summary:
        print("Warning: Handoff summary file is empty or not found. This is a required field.")
        # In a real scenario, we might exit here. For now, we'll allow it.

    # 4. Load analogies and session history
    analogies_registry = load_json(ANALOGIES_REGISTRY_FILE) or {}
    session_history = load_json(SESSION_HISTORY_FILE) or []

    # 5. Merge new data into the wisdom packet
    timestamp = datetime.now().isoformat()

    # Append the new summary
    wisdom_packet["session_summaries"].append({
        "timestamp": timestamp,
        "summary_text": summary,
        "key_decisions": decisions,
        "lessons_learned": lessons,
    })

    # Merge analogies
    wisdom_packet["analogies"].update(analogies_registry)

    # Append session history
    wisdom_packet["session_history"].extend(session_history)

    # Update metadata
    wisdom_packet["metadata"]["last_updated"] = timestamp
    wisdom_packet["metadata"]["total_sessions"] = len(wisdom_packet["session_summaries"])

    # 6. Atomic Write of the consolidated JSON packet
    os.makedirs(WISDOM_PACKET_DIR, exist_ok=True)
    packet_filename = f"wisdom_packet_{timestamp.replace(':', '-')}.json"
    packet_filepath = os.path.join(WISDOM_PACKET_DIR, packet_filename)

    try:
        with open(packet_filepath, 'w') as f:
            json.dump(wisdom_packet, f, indent=2)
        print(f"\nSuccessfully created consolidated wisdom packet: {packet_filepath}")
    except Exception as e:
        print(f"\nFATAL: Could not write wisdom packet. Handoff failed. Error: {e}")
        return

    # 7. Generate Markdown Handoff from the LATEST session data
    os.makedirs(HANDOFF_DIR, exist_ok=True)
    handoff_filename = f"{timestamp.replace(':', '-')}.md"
    handoff_filepath = os.path.join(HANDOFF_DIR, handoff_filename)

    md_content = f"# Handoff: {timestamp}\n\n"
    md_content += "## 1. Summary of Work\n"
    md_content += f"{summary}\n\n"
    md_content += "## 2. Key Decisions\n"
    for d in decisions:
        md_content += f"- {d}\n"
    md_content += "\n## 3. Lessons Learned\n"
    for l in lessons:
        md_content += f"- {l}\n"
    md_content += f"\n*This handoff was generated from the canonical wisdom packet: `{packet_filename}`*"

    try:
        with open(handoff_filepath, 'w') as f:
            f.write(md_content)
        print(f"Successfully generated markdown handoff: {handoff_filepath}")
    except Exception as e:
        print(f"Warning: Could not generate markdown handoff file. Error: {e}")

    # 8. Log this handoff as processed
    try:
        history_log_path = os.path.join(CONTEXT_DIR, 'history.log')
        log_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{log_timestamp} - Successfully processed handoff 'handoffs/{handoff_filename}'.\n"
        with open(history_log_path, 'a') as f:
            f.write(log_message)
        print(f"Successfully logged processing of {handoff_filename}")
    except Exception as e:
        print(f"Warning: Could not write to history log. Error: {e}")

    print("\n--- Automated Handoff Consolidation Complete ---")


if __name__ == "__main__":
    main()
