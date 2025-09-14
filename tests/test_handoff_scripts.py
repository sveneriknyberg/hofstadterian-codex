import os
import sys
import pytest
import json
from unittest.mock import patch

# Add the 'scripts' directory to the python path so we can import our scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

# Now we can import the script we want to test
import consolidate_handoff

@pytest.fixture
def setup_clean_env(tmp_path):
    """
    Creates a clean, temporary directory structure that mimics the project root
    for testing the non-interactive handoff script.
    """
    # Create root directories needed for the script
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "handoffs").mkdir()
    context_dir = (tmp_path / "context")
    context_dir.mkdir()

    # Create dummy context files that the script will read
    (context_dir / "handoff_summary.txt").write_text("Test summary of work.")
    (context_dir / "handoff_decisions.log").write_text("A test decision.")
    (context_dir / "handoff_lessons.log").write_text("A test lesson.")

    # The script under test will use this as its CWD.
    return tmp_path

def test_consolidate_handoff_end_to_end(setup_clean_env):
    """
    Tests if the non-interactive consolidate_handoff script successfully creates
    a wisdom packet and markdown handoff from files in the context/ directory.
    """
    project_root = setup_clean_env

    original_cwd = os.getcwd()
    # We change into the temp directory so the script uses it as the root.
    os.chdir(project_root)

    try:
        # The script is non-interactive, so we just run it directly.
        consolidate_handoff.main()
    finally:
        # Always change back to the original directory
        os.chdir(original_cwd)

    # --- Verification ---
    # 1. Verify that a wisdom packet was created
    artifacts_dir = project_root / "artifacts"
    created_packets = list(artifacts_dir.glob("wisdom_packet_*.json"))
    assert len(created_packets) == 1, "A single wisdom packet should have been created."

    packet_path = created_packets[0]
    with open(packet_path, 'r') as f:
        packet_data = json.load(f)

    # 2. Verify the contents of the wisdom packet (new v2.1 structure)
    assert packet_data["metadata"]["wisdom_packet_version"] == "2.1"

    # The new script creates a list of session summaries
    assert len(packet_data["session_summaries"]) == 1
    summary = packet_data["session_summaries"][0]

    assert summary["summary_text"] == "Test summary of work."
    assert summary["key_decisions"] == ["A test decision."]
    assert summary["lessons_learned"] == ["A test lesson."]

    # The session history is not currently part of the summary object.
    # This can be added as a future enhancement.

    # 3. Verify that a markdown handoff was also created
    handoffs_dir = project_root / "handoffs"
    created_handoffs = list(handoffs_dir.glob("*.md"))
    assert len(created_handoffs) == 1, "A single markdown handoff file should have been created."

    handoff_content = created_handoffs[0].read_text()
    assert "Test summary of work." in handoff_content
    assert "A test decision." in handoff_content
    assert "A test lesson." in handoff_content
    assert f"*This handoff was generated from the canonical wisdom packet: `{packet_path.name}`*" in handoff_content
