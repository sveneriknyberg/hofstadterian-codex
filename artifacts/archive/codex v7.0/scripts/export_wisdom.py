import json
import os
import argparse
import datetime

# --- Configuration ---
WISDOM_SOURCES = {
    "analogies": "analogies/registry.json",
    "lessons": "context/lessons.log",
    "decisions": "context/decisions.log",
    "workflows": "context/proven_workflows.json"
}
OUTPUT_DIR = "artifacts"

# --- Main Logic ---

def read_source_file(path):
    """Reads a source file, returning its content as a string."""
    if not os.path.exists(path):
        print(f"Warning: Source file not found, skipping: {path}")
        return None
    with open(path, 'r') as f:
        return f.read()

def export_wisdom(project_name):
    """Gathers wisdom from source files and bundles it into a packet."""
    print(f"Creating wisdom packet for project: {project_name}...")

    # --- Generate dynamic filename ---
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
    output_filename = f"wisdom_packet-{project_name}-{timestamp}.json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    wisdom_packet = {}

    for name, path in WISDOM_SOURCES.items():
        content = read_source_file(path)
        if content is None:
            continue

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
    with open(output_path, 'w') as f:
        json.dump(wisdom_packet, f, indent=2)

    print(f"Successfully created wisdom packet at: {output_path}")
    print(f"Included sources: {', '.join(wisdom_packet.keys())}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exports a Loop's wisdom into a portable JSON packet.")
    parser.add_argument(
        "--project_name",
        default="unnamed-loop",
        help="A descriptor for the project name to be included in the output filename."
    )
    args = parser.parse_args()
    export_wisdom(args.project_name)
