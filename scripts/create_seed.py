import os
import json
import base64
import datetime
import stat
import argparse

# --- Configuration ---
# Define the components of the Loop to be included in the seed.
ROOT_FILES_TO_INCLUDE = ["AGENTS.md", "LICENSE", ".gitignore"]
DIRS_TO_INCLUDE = ["scripts", "context", "analogies", "tests"]
OUTPUT_DIR = "artifacts"
SEED_FORMAT_VERSION = "1.0"

def should_be_executable(filepath):
    """Check if a file should be marked as executable."""
    return filepath.startswith('scripts/') and (filepath.endswith('.sh') or filepath.endswith('.py'))

def create_genesis_seed(project_name):
    """
    Gathers all necessary Loop components and packages them into a
    dynamically named genesis_seed.json file.
    """
    print(f"Starting Genesis Seed creation for project: {project_name}...")

    # --- Generate dynamic filename ---
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
    output_filename = f"genesis_seed-{project_name}-{timestamp}.json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    file_content_map = {}
    protocol = []

    # --- 1. Build Germination Protocol: Directory Creation ---
    protocol.append({"action": "log_message", "message": f"Starting Loop Germination Protocol v{SEED_FORMAT_VERSION}..."})
    protocol.append({"action": "create_directory", "path": "artifacts/"})
    all_dirs = set(DIRS_TO_INCLUDE)

    # --- 2. Gather files and build the file_content_map ---
    all_files = []
    for dir_name in DIRS_TO_INCLUDE:
        for root, dirs, files in os.walk(dir_name):
            for d in dirs:
                full_dir_path = os.path.join(root, d)
                normalized_dir_path = full_dir_path.replace(os.sep, '/')
                if "__pycache__" not in normalized_dir_path:
                    all_dirs.add(normalized_dir_path)

            for filename in files:
                if "__pycache__" in root:
                    continue
                filepath = os.path.join(root, filename)
                all_files.append(filepath)

    all_files.extend(ROOT_FILES_TO_INCLUDE)
    all_files.sort()

    for dir_path in sorted(list(all_dirs)):
        protocol.append({"action": "create_directory", "path": dir_path})

    # --- 3. Build Protocol: File Creation and populate map ---
    for filepath in all_files:
        if not os.path.exists(filepath):
            print(f"  [WARNING] File not found, skipping: {filepath}")
            continue

        try:
            with open(filepath, 'rb') as f:
                content_bytes = f.read()
            encoded_content = base64.b64encode(content_bytes).decode('utf-8')
            normalized_path = filepath.replace(os.sep, '/')
            file_content_map[normalized_path] = encoded_content
            protocol.append({"action": "create_file", "path": normalized_path})
            if should_be_executable(normalized_path):
                protocol.append({"action": "make_executable", "path": normalized_path})
        except Exception as e:
            print(f"  [ERROR] Could not process file {filepath}: {e}")

    # --- 4. Add Final Protocol Steps ---
    protocol.append({
        "action": "log_message",
        "message": "Germination complete. To initialize the new Loop, run: bash scripts/preflight_check.sh"
    })
    protocol.append({
        "action": "emergency_fallback",
        "instruction": "Protocol interpretation failed. To germinate, create 'scripts/germinate.py' from the file_content_map, make it executable, and run: python3 scripts/germinate.py --seed_file <seed_file_name>"
    })

    # --- 5. Assemble the final seed object ---
    seed_data = {
        "metadata": {
            "seed_format_version": SEED_FORMAT_VERSION,
            "project_name": project_name,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_loop_id": "oracle-loop-v1"
        },
        "germination_protocol": protocol,
        "file_content_map": file_content_map
    }

    # --- 6. Write the seed to file ---
    try:
        with open(output_path, 'w') as f:
            json.dump(seed_data, f, indent=2)
        print(f"Successfully created Genesis Seed at: {output_path}")
        print(f"Included {len(file_content_map)} files.")
    except Exception as e:
        print(f"[FATAL] Could not write to output file {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates a Genesis Seed file for a Strange Loop.")
    parser.add_argument(
        "--project_name",
        default="unnamed-loop",
        help="A descriptor for the project name to be included in the output filename."
    )
    args = parser.parse_args()
    create_genesis_seed(args.project_name)
