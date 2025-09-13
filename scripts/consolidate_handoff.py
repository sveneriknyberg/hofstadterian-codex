import json
import os
from datetime import datetime

# --- Configuration ---
WISDOM_PACKET_DIR = "artifacts"
HANDOFF_DIR = "handoffs"
SESSION_HISTORY_FILE = ".session_history.json"

# --- Helper functions for user input ---

def get_multiline_input(prompt):
    """Gets multiline input from the user, ending with 'END' on a new line."""
    print(f"\n> {prompt} (type 'END' on a new line when finished):")
    lines = []
    while True:
        try:
            line = input()
            if line == "END":
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)

def get_list_input(prompt, item_prefix):
    """Gets a list of simple items from the user."""
    print(f"\n> {prompt} (one item per line, type 'END' when finished):")
    items = []
    while True:
        try:
            line = input(f"{item_prefix} ")
            if line == "END":
                break
            if line:
                items.append(line)
        except EOFError:
            break
    return items

def get_roadmap_updates():
    """Gets structured roadmap updates from the user."""
    print("\n> List any roadmap updates (one item per line, type 'END' when finished):")
    updates = []
    while True:
        try:
            item_text = input("- ")
            if item_text == "END":
                break
            if not item_text:
                continue

            # Simple check for now. A more advanced version could ask for action type.
            updates.append({
                "action": "update", # Defaulting to a generic 'update'
                "item_text": item_text
            })
        except EOFError:
            break
    return updates

def get_new_analogies():
    """Gets structured new analogies from the user."""
    print("\n> List any new analogies discovered (type 'END' when finished):")
    analogies = []
    while True:
        try:
            name = input("Analogy Name (e.g., my_new_analogy): ")
            if name == "END":
                break
            if not name:
                continue

            rationale = get_multiline_input(f"Rationale for '{name}':")
            trigger = get_multiline_input(f"Trigger for '{name}':")

            analogies.append({
                "name": name,
                "rationale": rationale,
                "trigger": trigger
            })
        except EOFError:
            break
    return analogies

# --- Main Logic ---
def main():
    print("--- Starting Handoff Consolidation Process ---")

    # 1. Interactive Dialogue
    summary = get_multiline_input("Provide a brief, one-paragraph summary of the work accomplished.")
    decisions = get_list_input("List the key decisions made.", item_prefix="-")
    lessons = get_list_input("List the lessons learned.", item_prefix="-")
    roadmap_updates = get_roadmap_updates()
    new_analogies = get_new_analogies()

    # 2. Read Session History
    if os.path.exists(SESSION_HISTORY_FILE):
        with open(SESSION_HISTORY_FILE, 'r') as f:
            try:
                session_history = json.load(f)
            except json.JSONDecodeError:
                session_history = []
                print("Warning: Could not parse session history file. It will be empty in the packet.")
    else:
        session_history = []
        print("Warning: Session history file not found. It will be empty in the packet.")

    # 3. Assemble the Wisdom Packet
    timestamp = datetime.now().isoformat()
    wisdom_packet = {
        "metadata": {
            "wisdom_packet_version": "1.0",
            "timestamp_created": timestamp,
            "source_agent_id": os.environ.get("JULES_AGENT_ID", "jules"), # Get agent ID from env var if available
            "source_session_id": timestamp
        },
        "session_summary": {
            "summary_text": summary,
            "key_decisions": decisions,
            "lessons_learned": lessons,
        },
        "roadmap_updates": roadmap_updates,
        "new_analogies": new_analogies,
        "session_history": session_history
    }

    # 4. Atomic Write of JSON packet
    os.makedirs(WISDOM_PACKET_DIR, exist_ok=True)
    packet_filename = f"wisdom_packet_{timestamp.replace(':', '-')}.json"
    packet_filepath = os.path.join(WISDOM_PACKET_DIR, packet_filename)

    try:
        with open(packet_filepath, 'w') as f:
            json.dump(wisdom_packet, f, indent=2)
        print(f"\nSuccessfully created wisdom packet: {packet_filepath}")
    except Exception as e:
        print(f"\nFATAL: Could not write wisdom packet. Handoff failed. Error: {e}")
        return

    # 5. Generate Markdown Handoff from the packet
    os.makedirs(HANDOFF_DIR, exist_ok=True)
    handoff_filename = f"{timestamp.replace(':', '-')}.md"
    handoff_filepath = os.path.join(HANDOFF_DIR, handoff_filename)

    md_content = f"# Handoff: {timestamp}\n\n"
    md_content += "## 1. Summary of Work\n"
    md_content += f"{summary}\n\n"
    md_content += "## 2. Key Decisions\n"
    for d in decisions:
        md_content += f"- {d}\n"
    md_content += "\n"
    md_content += "## 3. Lessons Learned\n"
    for l in lessons:
        md_content += f"- {l}\n"
    md_content += "\n"
    if roadmap_updates:
        md_content += "## 4. Roadmap Updates\n"
        for u in roadmap_updates:
            md_content += f"- {u['item_text']}\n"
        md_content += "\n"
    if new_analogies:
        md_content += "## 5. New Analogies\n"
        for a in new_analogies:
            md_content += f"- **{a['name']}**\n"
            md_content += f"  - **Rationale:** {a['rationale']}\n"
            md_content += f"  - **Trigger:** {a['trigger']}\n"
        md_content += "\n"

    md_content += f"*This handoff was generated from the canonical wisdom packet: `{packet_filename}`*"

    try:
        with open(handoff_filepath, 'w') as f:
            f.write(md_content)
        print(f"Successfully generated markdown handoff: {handoff_filepath}")
    except Exception as e:
        print(f"Warning: Could not generate markdown handoff file. The canonical JSON packet was saved. Error: {e}")

    print("\n--- Handoff Consolidation Complete ---")


if __name__ == "__main__":
    main()
