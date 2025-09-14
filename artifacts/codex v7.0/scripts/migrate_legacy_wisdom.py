import json
import os
import re
from datetime import datetime, timezone

# Define file paths
HANDOFFS_DIR = 'handoffs'
ARTIFACTS_DIR = 'artifacts'
CONTEXT_DIR = 'context'
ANALOGIES_FILE = os.path.join('analogies', 'registry.json')
OUTPUT_FILE = os.path.join(ARTIFACTS_DIR, 'wisdom_packet_genesis.json')

def parse_markdown_handoff(content):
    """
    Parses the content of an old-style markdown handoff file.
    Returns a dictionary for the session summary and a dictionary for analogies.
    """
    summary = re.search(r'## 1\.\s*Summary of Work\n(.*?)\n## 2\.', content, re.DOTALL)
    decisions = re.search(r'## 2\.\s*Key Decisions\n(.*?)\n## 3\.', content, re.DOTALL)
    lessons = re.search(r'## 3\.\s*Lessons Learned\n(.*?)\n## 4\.', content, re.DOTALL)
    analogies_text = re.search(r'## 4\.\s*New Analogies\n(.*?)\n## 5\.', content, re.DOTALL)

    session_data = {
        "summary_text": summary.group(1).strip() if summary else "",
        "key_decisions": [d.strip('- ').strip() for d in decisions.group(1).strip().split('\n') if d.strip()] if decisions else [],
        "lessons_learned": [l.strip('- ').strip() for l in lessons.group(1).strip().split('\n') if l.strip()] if lessons else [],
    }

    analogies_found = {}
    if analogies_text and "N/A" not in analogies_text.group(1).strip():
        current_analogy = None
        current_analogy_data = {}
        for line in analogies_text.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith("- ANALOGY:"):
                if current_analogy: # Save the previous analogy
                    analogies_found[current_analogy] = current_analogy_data
                current_analogy = line.replace("- ANALOGY:", "").strip()
                current_analogy_data = {}
            elif line.startswith("- RATIONALE:") and current_analogy:
                current_analogy_data["rationale"] = line.replace("- RATIONALE:", "").strip()
            elif line.startswith("- TRIGGER:") and current_analogy:
                current_analogy_data["trigger"] = line.replace("- TRIGGER:", "").strip()
        if current_analogy: # Save the last analogy
            analogies_found[current_analogy] = current_analogy_data

    return session_data, analogies_found

def main():
    """
    Main function to perform the Great Consolidation.
    """
    print("--- Starting The Great Consolidation (v3) ---")

    # Initialize the new genesis wisdom packet
    genesis_packet = {
        "metadata": {
            "wisdom_packet_version": "3.0-genesis",
            "creation_date": datetime.now(timezone.utc).isoformat(),
            "description": "This packet is the result of a one-time 'Great Consolidation' of all legacy wisdom from the Strange Loop's history."
        },
        "session_summaries": [],
        "analogies": {},
        "proven_workflows": [],
    }

    processed_timestamps = set()

    # 1. Process modern wisdom packets first
    print("Step 1: Processing modern wisdom_packet.json files...")
    modern_packets = sorted([f for f in os.listdir(ARTIFACTS_DIR) if f.startswith('wisdom_packet_') and f.endswith('.json')])
    for packet_file in modern_packets:
        print(f"  - Reading {packet_file}")
        try:
            with open(os.path.join(ARTIFACTS_DIR, packet_file), 'r') as f:
                packet_data = json.load(f)

            for session in packet_data.get("session_summaries", []):
                ts = session.get("timestamp")
                if ts and ts not in processed_timestamps:
                    genesis_packet["session_summaries"].append(session)
                    processed_timestamps.add(ts)

            genesis_packet["analogies"].update(packet_data.get("analogies", {}))
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"    - WARNING: Could not process {packet_file}: {e}")


    # 2. Process old markdown handoffs
    print("\nStep 2: Processing legacy markdown handoffs...")
    handoff_files = sorted([f for f in os.listdir(HANDOFFS_DIR) if f.endswith('.md')])
    for handoff_file in handoff_files:
        print(f"  - Reading {handoff_file}")
        with open(os.path.join(HANDOFFS_DIR, handoff_file), 'r') as f:
            content = f.read()

        if "wisdom_packet" in content:
            print("    - Skipping modern handoff, data is in JSON.")
            continue

        ts_match = re.match(r'(\d{14})', handoff_file)
        timestamp = ts_match.group(1) if ts_match else "unknown_timestamp_" + handoff_file

        if timestamp not in processed_timestamps:
            print("    - Parsing legacy data...")
            session_data, analogies_found = parse_markdown_handoff(content)
            session_data["timestamp"] = timestamp

            genesis_packet["session_summaries"].append(session_data)
            genesis_packet["analogies"].update(analogies_found)
            processed_timestamps.add(timestamp)
        else:
            print("    - Skipping, session data already processed from JSON.")

    # 3. Consolidate standalone context files
    print("\nStep 3: Consolidating standalone context files...")
    try:
        with open(ANALOGIES_FILE, 'r') as f:
            print(f"  - Merging {ANALOGIES_FILE}")
            analogies_from_file = json.load(f)
            # Update only adds new ones, preserving existing ones
            # We iterate to avoid overwriting detailed entries with simple ones
            for key, value in analogies_from_file.items():
                if key not in genesis_packet["analogies"]:
                    genesis_packet["analogies"][key] = value
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"    - WARNING: Could not process {ANALOGIES_FILE}: {e}")

    # For other logs, we would add similar logic. For now, we assume
    # they are superseded by handoff content for this migration.

    # Sort session summaries by timestamp for chronological order
    genesis_packet["session_summaries"].sort(key=lambda x: x.get("timestamp", ""))

    # 4. Write the final genesis packet
    print(f"\nStep 4: Writing the consolidated genesis packet to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(genesis_packet, f, indent=2)

    print("\n--- The Great Consolidation (v3) is Complete ---")
    print(f"Successfully created {OUTPUT_FILE} with {len(genesis_packet['session_summaries'])} session summaries and {len(genesis_packet['analogies'])} analogies.")

if __name__ == "__main__":
    main()
