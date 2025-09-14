import os
import pytest
import subprocess
import tempfile

# --- Test Setup ---

@pytest.fixture
def setup_protocol_test_env(tmp_path):
    """
    Sets up a temporary directory that mimics the project structure
    for testing protocol scripts like preflight_check.sh.
    """
    project_root = tmp_path
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir()

    # Copy the actual scripts to be tested into the temp env
    # This makes the test self-contained
    subprocess.run(["cp", "scripts/preflight_check.sh", str(scripts_dir)])
    subprocess.run(["cp", "scripts/agent_bootstrap.sh", str(scripts_dir)])
    subprocess.run(["chmod", "+x", str(scripts_dir / "preflight_check.sh")])
    subprocess.run(["chmod", "+x", str(scripts_dir / "agent_bootstrap.sh")])

    # A dummy AGENTS.md is needed for the bootstrap script to run without error
    (project_root / "AGENTS.md").write_text("The Codex")
    (project_root / "context").mkdir() # for roadmap
    (project_root / "context/roadmap.md").touch()

    return project_root

# --- Tests ---

def test_preflight_check_in_barren_env(setup_protocol_test_env):
    """
    Tests if preflight_check.sh correctly runs the bootstrap process
    in a new, non-bootstrapped environment.
    """
    project_root = setup_protocol_test_env

    # 1. Act: Run the preflight check
    result = subprocess.run(
        ["bash", "scripts/preflight_check.sh"],
        cwd=project_root,
        capture_output=True,
        text=True
    )

    # 2. Assert
    assert result.returncode == 0, f"Preflight check failed in barren env:\n{result.stderr}"

    # It should detect a new session and run the bootstrap
    assert "[INFO] Bootstrap sentinel not found" in result.stdout
    assert "AGENT BOOTSTRAP PROTOCOL" in result.stdout # Output from bootstrap script

    # It should create the sentinel file
    assert (project_root / ".bootstrapped").exists()

    # It should give the final instruction to the agent
    assert "CRITICAL NEXT STEP: Your next action must be to read the AGENTS.md file" in result.stdout

    print("\n--- Test 'preflight_check_in_barren_env' PASSED ---")
    print("Preflight check correctly bootstrapped a new environment.")


def test_preflight_check_in_bootstrapped_env(setup_protocol_test_env):
    """
    Tests if preflight_check.sh correctly identifies an already
    bootstrapped environment and does not re-run the process.
    """
    project_root = setup_protocol_test_env

    # 1. Arrange: Create the sentinel file to simulate a bootstrapped env
    (project_root / ".bootstrapped").touch()

    # 2. Act: Run the preflight check
    result = subprocess.run(
        ["bash", "scripts/preflight_check.sh"],
        cwd=project_root,
        capture_output=True,
        text=True
    )

    # 3. Assert
    assert result.returncode == 0, f"Preflight check failed in bootstrapped env:\n{result.stderr}"

    # It should detect the existing sentinel
    assert "[PASS] Preflight check complete. Environment is already bootstrapped." in result.stdout

    # It should NOT run the bootstrap script again
    assert "AGENT BOOTSTRAP PROTOCOL" not in result.stdout

    # It should give the recommendation to re-read the codex
    assert "Recommendation: Re-read AGENTS.md" in result.stdout

    print("\n--- Test 'preflight_check_in_bootstrapped_env' PASSED ---")
    print("Preflight check correctly identified an existing environment.")
