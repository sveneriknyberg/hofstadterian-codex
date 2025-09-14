import os
import sys
import json
import pytest
import glob

# Add the 'scripts' directory to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from scripts import export_wisdom, import_wisdom, excavate_scratch

@pytest.fixture
def setup_wisdom_test_env(tmp_path):
    """Sets up a temporary environment for wisdom import/export testing."""
    project_root = tmp_path
    # Create source directories
    (project_root / "analogies").mkdir()
    (project_root / "context").mkdir()
    (project_root / "artifacts").mkdir() # For output

    # Change CWD to the temp root
    original_cwd = os.getcwd()
    os.chdir(project_root)
    yield project_root
    os.chdir(original_cwd)

def test_export_wisdom_with_project_name(setup_wisdom_test_env):
    """Tests the successful creation of a named wisdom packet."""
    project_root = setup_wisdom_test_env
    project_name = "test-export"

    # 1. Create mock source files
    (project_root / "analogies" / "registry.json").write_text('{"analogy1": {"rationale": "r1"}}')
    (project_root / "context" / "lessons.log").write_text("lesson1")

    # 2. Run the export script's main function
    export_wisdom.export_wisdom(project_name=project_name)

    # 3. Assert the output
    created_files = glob.glob(f"artifacts/wisdom_packet-{project_name}-*.json")
    assert len(created_files) == 1, "Expected one named wisdom packet to be created."

    packet_path = created_files[0]
    with open(packet_path, 'r') as f:
        packet_data = json.load(f)

    assert "analogies" in packet_data
    assert "lessons" in packet_data
    print(f"Successfully created and validated named wisdom packet: {packet_path}")


def test_import_wisdom_with_path_argument(setup_wisdom_test_env):
    """Tests the successful import of a wisdom packet passed as an argument."""
    project_root = setup_wisdom_test_env
    packet_name = "wisdom_packet-test-import-12345.json"
    packet_path = project_root / packet_name

    # 1. Create a mock wisdom packet
    packet_data = {
        "analogies": {"new_analogy": {"rationale": "new_r"}},
        "lessons": ["new_lesson", "lesson1"],
    }
    packet_path.write_text(json.dumps(packet_data))

    # 2. Create mock local files
    (project_root / "analogies" / "registry.json").write_text('{"local_analogy": {}}')
    (project_root / "context" / "lessons.log").write_text("lesson1\n")

    # 3. Run the import script's main function
    import_wisdom.import_wisdom(packet_path=str(packet_path))

    # 4. Assert the merged results
    analogies_path = project_root / "analogies" / "registry.json"
    with open(analogies_path, 'r') as f:
        analogies_data = json.load(f)
    assert "local_analogy" in analogies_data
    assert "new_analogy" in analogies_data

    lessons_path = project_root / "context" / "lessons.log"
    with open(lessons_path, 'r') as f:
        lessons_data = f.read()
    assert "new_lesson" in lessons_data
    assert lessons_data.count("lesson1") == 1

    # 5. Assert the packet was renamed
    assert not packet_path.exists()
    assert (project_root / packet_name.replace(".json", ".imported")).exists()
    print("Successfully imported wisdom from a dynamically named packet.")


@pytest.fixture
def setup_excavation_test_env(tmp_path):
    """Sets up a temporary environment for excavation testing."""
    project_root = tmp_path
    (project_root / "handoffs").mkdir()
    (project_root / "scratch").mkdir()

    original_cwd = os.getcwd()
    os.chdir(project_root)
    yield project_root
    os.chdir(original_cwd)

def test_excavate_scratch_finds_match(setup_excavation_test_env, capsys):
    """
    Tests that the excavation script can find a relevant scratch file
    based on keywords in an unresolved issue.
    """
    project_root = setup_excavation_test_env

    # 1. Arrange: Create test data
    handoff_content = """
## 6. Unresolved Issues & Next Steps
- The `zorp` module is failing on import. We need to investigate the `zorp.py` file.
"""
    (project_root / "handoffs" / "20251010.md").write_text(handoff_content)

    scratch_content = "import zorp"
    (project_root / "scratch" / "zorp_import_fix_idea.py").write_text(scratch_content)

    # 2. Act: Run the script
    excavate_scratch.main()

    # 3. Assert: Check the output
    captured = capsys.readouterr()
    assert "[!] Potential Match Found!" in captured.out
    assert "The `zorp` module is failing on import" in captured.out
    assert "scratch/zorp_import_fix_idea.py" in captured.out

def test_excavate_scratch_no_match(setup_excavation_test_env, capsys):
    """
    Tests that the script reports no matches when keywords don't overlap.
    """
    project_root = setup_excavation_test_env

    # 1. Arrange: Create non-matching test data
    handoff_content = "## 6. Unresolved Issues & Next Steps\n- The database connection is timing out."
    (project_root / "handoffs" / "20251011.md").write_text(handoff_content)
    (project_root / "scratch" / "some_unrelated_script.js").write_text("console.log('hello');")

    # 2. Act: Run the script
    excavate_scratch.main()

    # 3. Assert: Check the output
    captured = capsys.readouterr()
    assert "[!] Potential Match Found!" not in captured.out
    assert "No correlations found" in captured.out
