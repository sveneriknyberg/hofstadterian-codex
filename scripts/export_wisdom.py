import json
import os

# --- Configuration ---
WISDOM_SOURCES = {
    "analogies": "analogies/registry.json",
    "lessons": "context/lessons.log",
    "decisions": "context/decisions.log",
    "workflows": "context/proven_workflows.json"
}
OUTPUT_PACKET_FILE = "wisdom_packet.json"

# --- Main Logic ---

def read_source_file(path):
    """Reads a source file, returning its content as a string."""
    if not os.path.exists(path):
        print(f"Warning: Source file not found, skipping: {path}")
        return None
    with open(path, 'r') as f:
        return f.read()

def main():
    """Gathers wisdom from source files and bundles it into a packet."""
    print("Creating wisdom packet...")
    wisdom_packet = {}

    for name, path in WISDOM_SOURCES.items():
        content = read_source_file(path)
        if content is None:
            continue

        # For JSON files, parse them to ensure they are valid
        # and store them as objects. For others, store as raw text.
        if path.endswith('.json'):
            try:
                wisdom_packet[name] = json.loads(content)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON from {path}, skipping.")
                continue
        else:
            wisdom_packet[name] = content.strip().split('\n')

    if not wisdom_packet:
        print("No wisdom sources found or all were empty. No packet created.")
        return

    # Write the bundled wisdom to the output file
    with open(OUTPUT_PACKET_FILE, 'w') as f:
        json.dump(wisdom_packet, f, indent=2)

    print(f"Successfully created wisdom packet at: {OUTPUT_PACKET_FILE}")
    print(f"Included sources: {', '.join(wisdom_packet.keys())}")


if __name__ == "__main__":
    main()
