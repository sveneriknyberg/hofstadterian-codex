import os
import json
import base64
import argparse
from datetime import datetime, timezone
import gzip

ROOT_FILES_TO_INCLUDE = ["AGENTS.md", ".gitignore", "LICENSE", "preflight_check.sh"]
DIRS_TO_INCLUDE = ["scripts", "wisdom", "handoffs"]
OUTPUT_DIR = "artifacts"
SEED_FORMAT_VERSION = "1.4"

def should_be_executable(filepath):
    return filepath.startswith('scripts/') or filepath.endswith('.sh')

def create_genesis_seed(project_name):
    file_content_map = {}
    protocol = [{"action": "log_message", "message": f"Starting Loop Germination Protocol v1.4..."}]
    all_files = []

    all_dirs = set(DIRS_TO_INCLUDE)
    for dir_name in DIRS_TO_INCLUDE:
        if not os.path.isdir(dir_name): continue
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

    for dir_path in sorted(list(all_dirs)):
        protocol.append({"action": "create_directory", "path": dir_path})

    for filepath in sorted(list(set(all_files))):
        if not os.path.exists(filepath):
            continue

        normalized_path = filepath.replace(os.sep, '/')
        if normalized_path == "LICENSE":
            protocol.append({
                "action": "fetch_file_from_url",
                "path": "LICENSE",
                "url": "https://www.gnu.org/licenses/gpl-3.0.txt"
            })
            continue

        with open(filepath, 'rb') as f:
            content_bytes = f.read()

        compressed_bytes = gzip.compress(content_bytes)
        encoded_content = base64.b64encode(compressed_bytes).decode('utf-8')
        file_content_map[normalized_path] = encoded_content

        protocol.append({"action": "create_file", "path": normalized_path})
        if should_be_executable(normalized_path):
            protocol.append({"action": "make_executable", "path": normalized_path})

    protocol.append({
        "action": "log_message",
        "message": "Germination complete. To initialize the new Loop, run: bash preflight_check.sh"
    })

    seed_data = {
        "metadata": {
            "seed_format_version": SEED_FORMAT_VERSION,
            "project_name": project_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_loop_id": "oracle-loop-v1",
            "compression": "gzip+base64",
            "version_notes": "v12.4 - Corrected by Gemini. Restored the critical scripts/pre_submit_check.sh to the protocol."
        },
        "germination_protocol": protocol,
        "file_content_map": file_content_map
    }

    timestamp_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    output_filename = f"genesis_seed-{project_name}-{timestamp_str}.json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(seed_data, f, indent=2)

    print(f"Successfully created Genesis Seed at: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates a Genesis Seed file for the Loop.")
    parser.add_argument("--project_name", default="hofstadterian-codex", help="Project name to embed in the seed.")
    args = parser.parse_args()
    create_genesis_seed(args.project_name)
