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
    for testing the handoff script.
    """
    # Create root directories needed for the script
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "handoffs").mkdir()

    # Create a dummy session history file
    dummy_history = [{"command": "ls", "exit_code": 0}]
    with open(tmp_path / ".session_history.json", 'w') as f:
        json.dump(dummy_history, f)

    # The script under test will use this as its CWD.
    return tmp_path

def test_consolidate_handoff_end_to_end(setup_clean_env):
    """
    Tests if the consolidate_handoff script successfully creates a wisdom packet
    and a corresponding markdown handoff file based on mocked user input.
    """
    project_root = setup_clean_env

    # Mock a sequence of user inputs. Each string is one call to input().
    user_input_sequence = [
        # Summary
        "Test summary of work.",
        "END",
        # Decisions
        "A test decision.",
        "END",
        # Lessons
        "A test lesson.",
        "END",
        # Roadmap Updates
        "A test roadmap update.",
        "END",
        # New Analogies
        "test_analogy",
        "This is the rationale.",
        "END",
        "This is the trigger.",
        "END",
        "END", # Final 'END' to stop the analogy loop
    ]

    original_cwd = os.getcwd()
    # We change into the temp directory so the script uses it as the root.
    os.chdir(project_root)

    try:
        # We patch 'builtins.input' to simulate the user typing answers.
        with patch('builtins.input', side_effect=user_input_sequence):
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

    # 2. Verify the contents of the wisdom packet
    assert packet_data["metadata"]["wisdom_packet_version"] == "1.0"
    summary = packet_data["session_summary"]
    assert summary["summary_text"] == "Test summary of work."
    assert summary["key_decisions"] == ["A test decision."]
    assert summary["lessons_learned"] == ["A test lesson."]
    assert packet_data["roadmap_updates"][0]["item_text"] == "A test roadmap update."
    analogy = packet_data["new_analogies"][0]
    assert analogy["name"] == "test_analogy"
    assert analogy["rationale"] == "This is the rationale."
    assert analogy["trigger"] == "This is the trigger."
    assert len(packet_data["session_history"]) == 1
    assert packet_data["session_history"][0]["command"] == "ls"

    # 3. Verify that a markdown handoff was also created
    handoffs_dir = project_root / "handoffs"
    created_handoffs = list(handoffs_dir.glob("*.md"))
    assert len(created_handoffs) == 1, "A single markdown handoff file should have been created."

    handoff_content = created_handoffs[0].read_text()
    assert "Test summary of work." in handoff_content
    assert "- A test decision." in handoff_content
    assert "- A test lesson." in handoff_content
    assert "## 4. Roadmap Updates" in handoff_content
    assert "- A test roadmap update." in handoff_content
    assert "## 5. New Analogies" in handoff_content
    assert "**test_analogy**" in handoff_content
    assert "Rationale:** This is the rationale." in handoff_content
    assert f"*This handoff was generated from the canonical wisdom packet: `{packet_path.name}`*" in handoff_content
