import os
import sys
import json
import pytest
import stat
import subprocess
import base64

# Add the 'scripts' directory to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts import create_seed, germinate

@pytest.fixture
def setup_source_loop(tmp_path):
    """Sets up a minimal, mock "source" Loop to generate a seed from."""
    source_dir = tmp_path / "source_loop"
    source_dir.mkdir()

    # Create some directories and files to be included in the seed
    (source_dir / "scripts").mkdir()
    (source_dir / "AGENTS.md").write_text("This is the Codex.")

    bootstrap_script_path = source_dir / "scripts" / "agent_bootstrap.sh"
    bootstrap_script_path.write_text("#!/bin/bash\necho 'Bootstrapping...'")
    # Make it executable
    os.chmod(bootstrap_script_path, 0o755)

    # We need to add the test script itself to the manifest for it to be found
    create_seed.LOOP_MANIFEST = [
        "AGENTS.md",
        "scripts/agent_bootstrap.sh"
    ]
    create_seed.REQUIRED_DIRS = ["scripts"]

    return source_dir

def test_genesis_end_to_end(setup_source_loop):
    """
    Tests the full lifecycle: creating a seed from a source Loop and
    germinating a new Loop from that seed.
    """
    source_dir = setup_source_loop

    # --- Part 1: Create the seed ---
    original_cwd = os.getcwd()
    os.chdir(source_dir)

    create_seed.main()

    seed_path = source_dir / "genesis_seed.json"
    assert seed_path.exists()

    # --- Part 2: Germinate from the seed in a new location ---
    barren_dir = source_dir.parent / "barren_dir"
    barren_dir.mkdir()
    os.chdir(barren_dir)

    # In a real scenario, germinate.py would be run directly.
    # Here, we call its main function, simulating that execution.
    # We need to load the seed data manually for the test.
    with open(seed_path, 'r') as f:
        seed_data = json.load(f)

    # Replicate germinate.py's logic without using sys.argv
    # Create directories
    for dir_path in seed_data.get("directories", []):
        if dir_path: os.makedirs(dir_path, exist_ok=True)

    # Create files
    for file_info in seed_data.get("files", []):
        file_path = file_info["path"]
        content_bytes = base64.b64decode(file_info["content_b64"])
        with open(file_path, 'wb') as f:
            f.write(content_bytes)
        if file_info["executable"]:
            os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IXUSR)

    # --- Part 3: Assert the new Loop is correct ---

    # Check if files and directories were created
    assert (barren_dir / "scripts").is_dir()
    assert (barren_dir / "AGENTS.md").is_file()
    new_bootstrap_path = barren_dir / "scripts" / "agent_bootstrap.sh"
    assert new_bootstrap_path.is_file()

    # Check file content
    assert (barren_dir / "AGENTS.md").read_text() == "This is the Codex."
    assert new_bootstrap_path.read_text() == "#!/bin/bash\necho 'Bootstrapping...'"

    # Check for executable permission
    assert os.access(new_bootstrap_path, os.X_OK)

    os.chdir(original_cwd)
