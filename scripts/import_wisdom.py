import json
import os

# --- Configuration ---
INPUT_PACKET_FILE = "wisdom_packet.json"
IMPORTED_PACKET_FILE = "wisdom_packet.imported"

WISDOM_TARGETS = {
    "analogies": "analogies/registry.json",
    "lessons": "context/lessons.log",
    "decisions": "context/decisions.log",
    "workflows": "context/proven_workflows.json"
}

# --- Helper Functions ---

def load_json_target(path):
    """Loads a JSON file, returning an empty dict/list if it doesn't exist."""
    if not os.path.exists(path):
        return [] if "workflows" in path else {}
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return [] if "workflows" in path else {}

def save_json_target(path, data):
    """Saves data to a JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def append_log_target(path, new_lines):
    """Appends unique lines to a log file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing_lines = set()
    if os.path.exists(path):
        with open(path, 'r') as f:
            existing_lines = set(line.strip() for line in f)

    with open(path, 'a') as f:
        for line in new_lines:
            if line.strip() and line.strip() not in existing_lines:
                f.write(line.strip() + '\n')

# --- Main Logic ---

def main():
    """Reads a wisdom packet and merges its contents into the current Loop."""
    if not os.path.exists(INPUT_PACKET_FILE):
        print("No wisdom packet found. Nothing to import.")
        return

    print(f"Importing wisdom from {INPUT_PACKET_FILE}...")
    with open(INPUT_PACKET_FILE, 'r') as f:
        wisdom_packet = json.load(f)

    # Import analogies (dictionary merge)
    if "analogies" in wisdom_packet:
        local_analogies = load_json_target(WISDOM_TARGETS["analogies"])
        local_analogies.update(wisdom_packet["analogies"])
        save_json_target(WISDOM_TARGETS["analogies"], local_analogies)
        print(f"  - Merged {len(wisdom_packet['analogies'])} analogies.")

    # Import workflows (list merge, avoiding duplicates)
    if "workflows" in wisdom_packet:
        local_workflows = load_json_target(WISDOM_TARGETS["workflows"])
        existing_timestamps = {wf.get("success_timestamp") for wf in local_workflows}
        new_workflows_added = 0
        for wf in wisdom_packet["workflows"]:
            if wf.get("success_timestamp") not in existing_timestamps:
                local_workflows.append(wf)
                new_workflows_added += 1
        save_json_target(WISDOM_TARGETS["workflows"], local_workflows)
        print(f"  - Imported {new_workflows_added} new proven workflows.")

    # Import logs (line append, avoiding duplicates)
    for name in ["lessons", "decisions"]:
        if name in wisdom_packet:
            append_log_target(WISDOM_TARGETS[name], wisdom_packet[name])
            print(f"  - Appended new entries to {name} log.")

    # Rename the packet to prevent re-import
    os.rename(INPUT_PACKET_FILE, IMPORTED_PACKET_FILE)
    print(f"\nWisdom import complete. Renamed packet to {IMPORTED_PACKET_FILE}.")


if __name__ == "__main__":
    main()
