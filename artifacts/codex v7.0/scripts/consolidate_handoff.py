import json
import os
import glob
import subprocess
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
    if not os.path.exists(filepath): return []
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def read_file_content(filepath):
    if not os.path.exists(filepath): return ""
    with open(filepath, 'r') as f: return f.read().strip()

def load_json(filepath):
    if not os.path.exists(filepath): return None
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON file '{filepath}'.")
            return None

def find_latest_wisdom_packet():
    list_of_files = glob.glob(os.path.join(WISDOM_PACKET_DIR, 'wisdom_packet_*.json'))
    if not list_of_files: return None
    return max(list_of_files, key=os.path.getctime)

# --- Main Logic ---
def main():
    print("--- Starting Automated Handoff Consolidation Process ---")

    # 1. Load the latest wisdom packet
    latest_packet_path = find_latest_wisdom_packet()
    if latest_packet_path:
        print(f"Loading previous wisdom from: {latest_packet_path}")
        wisdom_packet = load_json(latest_packet_path) or {}
    else:
        print("No previous wisdom packet found. Creating a new one.")
        wisdom_packet = {}

    # 2. Initialize sections
    wisdom_packet.setdefault("metadata", {"wisdom_packet_version": "2.1"}) # Version bump
    wisdom_packet.setdefault("session_summaries", [])
    wisdom_packet.setdefault("analogies", {})
    wisdom_packet.setdefault("proven_workflows", [])
    wisdom_packet.setdefault("semantic_insights", []) # New section
    wisdom_packet.setdefault("session_history", [])

    # 3. Load new session data
    summary = read_file_content(INPUT_SUMMARY_FILE)
    decisions = read_file_lines(INPUT_DECISIONS_FILE)
    lessons = read_file_lines(INPUT_LESSONS_FILE)

    # 4. Load analogies and session history
    analogies_registry = load_json(ANALOGIES_REGISTRY_FILE) or {}
    session_history = load_json(SESSION_HISTORY_FILE) or []

    # 5. Run analyzers to process the session history
    print("\n--- Running Analyzers ---")
    try:
        print("Running workflow analyzer...")
        subprocess.run(["python3", "scripts/workflow_analyzer.py"], check=True, capture_output=True, text=True)
        print("Workflow analysis complete.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Warning: Workflow analyzer script failed. Error: {getattr(e, 'stderr', e)}")

    try:
        print("Running semantic analyzer...")
        subprocess.run(["python3", "scripts/semantic_analyzer.py"], check=True, capture_output=True, text=True)
        print("Semantic analysis complete.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Warning: Semantic analyzer script failed. Error: {getattr(e, 'stderr', e)}")


    # 6. Load the updated artifacts from analyzers
    proven_workflows_file = os.path.join(CONTEXT_DIR, "proven_workflows.json")
    proven_workflows = load_json(proven_workflows_file) or []
    semantic_insights_file = os.path.join(CONTEXT_DIR, "semantic_insights.json") # New
    semantic_insights = load_json(semantic_insights_file) or [] # New


    # 7. Merge new data into the wisdom packet
    timestamp = datetime.now().isoformat()
    wisdom_packet["session_summaries"].append({
        "timestamp": timestamp,
        "summary_text": summary,
        "key_decisions": decisions,
        "lessons_learned": lessons,
    })
    wisdom_packet["analogies"].update(analogies_registry)
    wisdom_packet["proven_workflows"] = proven_workflows # Overwrite with latest
    wisdom_packet["semantic_insights"] = semantic_insights # Overwrite with latest
    wisdom_packet["session_history"].extend(session_history)
    wisdom_packet["metadata"]["last_updated"] = timestamp
    wisdom_packet["metadata"]["total_sessions"] = len(wisdom_packet["session_summaries"])

    # 8. Atomic Write of the consolidated JSON packet
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

    # 9. Generate Markdown Handoff
    os.makedirs(HANDOFF_DIR, exist_ok=True)
    handoff_filename = f"{timestamp.replace(':', '-')}.md"
    handoff_filepath = os.path.join(HANDOFF_DIR, handoff_filename)
    md_content = f"# Handoff: {timestamp}\n\n## 1. Summary of Work\n{summary}\n\n## 2. Key Decisions\n"
    for d in decisions: md_content += f"- {d}\n"
    md_content += "\n## 3. Lessons Learned\n"
    for l in lessons: md_content += f"- {l}\n"
    md_content += f"\n*This handoff was generated from the canonical wisdom packet: `{packet_filename}`*"
    try:
        with open(handoff_filepath, 'w') as f: f.write(md_content)
        print(f"Successfully generated markdown handoff: {handoff_filepath}")
    except Exception as e: print(f"Warning: Could not generate markdown handoff file. Error: {e}")

    # 10. Log this handoff as processed
    try:
        history_log_path = os.path.join(CONTEXT_DIR, 'history.log')
        log_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{log_timestamp} - Successfully processed handoff 'handoffs/{handoff_filename}'.\n"
        with open(history_log_path, 'a') as f: f.write(log_message)
        print(f"Successfully logged processing of {handoff_filename}")
    except Exception as e: print(f"Warning: Could not write to history log. Error: {e}")

    print("\n--- Automated Handoff Consolidation Complete ---")


if __name__ == "__main__":
    main()
