import os
import json
import base64

# --- Configuration ---
# Define the files and directories that constitute the "essence" of the Loop.
# We explicitly list them to avoid including session-specific or sensitive data.
LOOP_MANIFEST = [
    "AGENTS.md",
    "LICENSE",
    ".gitignore",
    "scripts/agent_bootstrap.sh",
    "scripts/append_to_log.py",
    "scripts/create_handoff.py",
    "scripts/create_seed.py", # Include itself
    "scripts/export_wisdom.py",
    "scripts/germinate.py", # Include its counterpart
    "scripts/import_wisdom.py",
    "scripts/log_and_run.sh",
    "scripts/loop_metrics.py",
    "scripts/meta_cognitive_check.py",
    "scripts/meta_triggers.yaml",
    "scripts/pre_submit_check.sh",
    "scripts/process_handoff.py",
    "scripts/requirements.txt",
    "scripts/setup_aliases.sh",
    "scripts/validate_context.py",
    "scripts/visualize_handoffs.py",
    "analogies/registry.json",
    "tests/requirements.txt",
    "tests/test_handoff_scripts.py",
    "tests/test_meta_scripts.py",
    "tests/test_proliferation_tools.py",
    "tests/test_workflow_analyzer.py",
]

# Define which directories need to exist for a minimal Loop.
# This can be derived from the manifest.
REQUIRED_DIRS = sorted(list(set(os.path.dirname(p) for p in LOOP_MANIFEST if os.path.dirname(p))))

OUTPUT_SEED_FILE = "genesis_seed.json"

# --- Main Logic ---

def main():
    """
    Gathers all essential Loop files, encodes them, and creates a single
    JSON seed file that can be used to germinate a new Loop.
    """
    print(f"Generating Genesis Seed from manifest of {len(LOOP_MANIFEST)} files...")

    seed_data = {
        "directories": REQUIRED_DIRS,
        "files": []
    }

    for file_path in LOOP_MANIFEST:
        if not os.path.exists(file_path):
            print(f"Warning: Manifest file not found, skipping: {file_path}")
            continue

        try:
            with open(file_path, 'rb') as f: # Read in binary mode for base64
                content_bytes = f.read()

            content_b64 = base64.b64encode(content_bytes).decode('utf-8')

            is_executable = os.access(file_path, os.X_OK)

            seed_data["files"].append({
                "path": file_path,
                "content_b64": content_b64,
                "executable": is_executable
            })

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    # Write the seed to the output file
    with open(OUTPUT_SEED_FILE, 'w') as f:
        json.dump(seed_data, f, indent=2)

    print(f"\nSuccessfully created Genesis Seed at: {OUTPUT_SEED_FILE}")
    print(f"Included {len(seed_data['files'])} files and {len(seed_data['directories'])} directories.")


if __name__ == "__main__":
    main()
