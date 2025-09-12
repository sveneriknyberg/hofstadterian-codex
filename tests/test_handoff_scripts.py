import os
import sys
import pytest
from unittest.mock import patch

# Add the 'scripts' directory to the python path so we can import our scripts
# This allows the test runner to find the modules.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

# Now we can import the scripts we want to test
import create_handoff
import process_handoff

@pytest.fixture
def setup_clean_env(tmp_path):
    """
    Creates a clean, temporary directory structure that mimics the project root.
    The scripts under test will use this as their CWD.
    """
    # Create root directories
    (tmp_path / "handoffs").mkdir()
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    (tmp_path / "scripts").mkdir() # Scripts need to find each other

    # Create necessary empty log files
    (context_dir / "decisions.log").touch()
    (context_dir / "lessons.log").touch()
    (context_dir / "history.log").touch()
    (context_dir / "roadmap.md").touch()

    # The actual scripts from the repo will be used, but they will operate
    # within this temporary directory because we chdir into it.
    return tmp_path

def test_create_and_process_handoff_end_to_end(setup_clean_env):
    """
    Tests if the create_handoff script successfully creates a handoff file
    and then if that file is processed correctly, updating the logs.
    This is an end-to-end test for the core handoff loop.
    """
    project_root = setup_clean_env

    # Mock user inputs for the script's prompts.
    # The create_handoff.py script uses the same multiline input function
    # for all sections, which always terminates with "END".
    user_inputs = [
        # 1. Summary
        "Test summary of work.", "END",
        # 2. Decisions
        "- DECISION: A test decision.", "END",
        # 3. Lessons
        "- LESSON: A test lesson.", "END",
        # 4. Analogies
        "N/A", "END",
        # 5. Roadmap
        "- ROADMAP: A test roadmap update.", "END",
        # 6. Next Steps
        "Test unresolved issues.", "END",
    ]

    original_cwd = os.getcwd()
    # We change into the temp directory so the scripts use it as the root.
    # This is the key to making the original scripts testable.
    os.chdir(project_root)

    # We need to copy the original scripts into the temp dir so the subprocess can find them
    original_scripts_dir = os.path.dirname(sys.modules['create_handoff'].__file__)
    for script_name in ['create_handoff.py', 'process_handoff.py']:
        original_path = os.path.join(original_scripts_dir, script_name)
        with open(original_path, 'r') as f:
            content = f.read()
        temp_script_path = project_root / "scripts" / script_name
        with open(temp_script_path, 'w') as f:
            f.write(content)

    try:
        with patch('builtins.input', side_effect=user_inputs):
            create_handoff.main()
    finally:
        # Always change back to the original directory
        os.chdir(original_cwd)

    # --- Verification ---
    # 1. Verify that a handoff file was created in the temp directory
    handoffs_dir = project_root / "handoffs"
    created_files = list(handoffs_dir.glob("*.md"))
    assert len(created_files) == 1, "A single handoff file should have been created."

    handoff_content = created_files[0].read_text()
    assert "Test summary of work." in handoff_content
    assert "- DECISION: A test decision." in handoff_content

    # 2. Verify that the context logs were updated by the processing step
    context_dir = project_root / "context"
    decision_log = (context_dir / "decisions.log").read_text()
    lesson_log = (context_dir / "lessons.log").read_text()
    roadmap_log = (context_dir / "roadmap.md").read_text()
    history_log = (context_dir / "history.log").read_text()

    # The processing script strips the 'DECISION:' prefix, so we assert the content only.
    assert "A test decision." in decision_log
    # The processing script strips the 'LESSON:' prefix.
    assert "A test lesson." in lesson_log
    # The roadmap processing keeps a '-' prefix.
    assert "- A test roadmap update." in roadmap_log
    assert ".md" in history_log, "The processed handoff should be recorded in the history log."
