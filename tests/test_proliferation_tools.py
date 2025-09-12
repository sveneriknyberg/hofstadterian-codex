import os
import sys
import json
import pytest

# Add the 'scripts' directory to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts import export_wisdom, import_wisdom, excavate_scratch

@pytest.fixture
def setup_wisdom_test_env(tmp_path):
    """Sets up a temporary environment for wisdom import/export testing."""
    project_root = tmp_path
    # Create source directories
    (project_root / "analogies").mkdir()
    (project_root / "context").mkdir()

    # Change CWD to the temp root
    original_cwd = os.getcwd()
    os.chdir(project_root)
    yield project_root
    os.chdir(original_cwd)

def test_export_wisdom(setup_wisdom_test_env):
    """Tests the successful creation of a wisdom packet."""
    project_root = setup_wisdom_test_env

    # 1. Create mock source files
    (project_root / "analogies" / "registry.json").write_text('{"analogy1": {"rationale": "r1"}}')
    (project_root / "context" / "lessons.log").write_text("lesson1\nlesson2")
    (project_root / "context" / "decisions.log").write_text("decision1")
    (project_root / "context" / "proven_workflows.json").write_text('[{"name": "wf1"}]')

    # 2. Run the export script
    export_wisdom.main()

    # 3. Assert the output
    packet_path = project_root / "wisdom_packet.json"
    assert packet_path.exists()
    with open(packet_path, 'r') as f:
        packet_data = json.load(f)

    assert "analogies" in packet_data
    assert packet_data["analogies"]["analogy1"]["rationale"] == "r1"
    assert "lessons" in packet_data
    assert "lesson1" in packet_data["lessons"]
    assert "decisions" in packet_data
    assert "decision1" in packet_data["decisions"]
    assert "workflows" in packet_data
    assert packet_data["workflows"][0]["name"] == "wf1"

def test_import_wisdom(setup_wisdom_test_env):
    """Tests the successful import and merging of a wisdom packet."""
    project_root = setup_wisdom_test_env

    # 1. Create a mock wisdom packet
    packet_data = {
        "analogies": {"new_analogy": {"rationale": "new_r"}},
        "lessons": ["new_lesson", "lesson1"], # "lesson1" is a duplicate
        "decisions": ["new_decision"],
        "workflows": [{"success_timestamp": "T01", "name": "new_wf"}]
    }
    (project_root / "wisdom_packet.json").write_text(json.dumps(packet_data))

    # 2. Create mock local files that already have some content
    (project_root / "analogies" / "registry.json").write_text('{"local_analogy": {}}')
    (project_root / "context" / "lessons.log").write_text("lesson1\n")
    (project_root / "context" / "decisions.log").write_text("") # empty log
    (project_root / "context" / "proven_workflows.json").write_text('[]')

    # 3. Run the import script
    import_wisdom.main()

    # 4. Assert the merged results
    # Analogies (dict merge)
    analogies_path = project_root / "analogies" / "registry.json"
    with open(analogies_path, 'r') as f:
        analogies_data = json.load(f)
    assert "local_analogy" in analogies_data
    assert "new_analogy" in analogies_data

    # Lessons (append unique)
    lessons_path = project_root / "context" / "lessons.log"
    with open(lessons_path, 'r') as f:
        lessons_data = f.read()
    assert "lesson1" in lessons_data
    assert "new_lesson" in lessons_data
    assert lessons_data.count("lesson1") == 1 # Check for no duplicates

    # Workflows (append unique)
    workflows_path = project_root / "context" / "proven_workflows.json"
    with open(workflows_path, 'r') as f:
        workflows_data = json.load(f)
    assert len(workflows_data) == 1
    assert workflows_data[0]["name"] == "new_wf"

    # 5. Assert the packet was renamed
    assert not (project_root / "wisdom_packet.json").exists()
    assert (project_root / "wisdom_packet.imported").exists()


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
## 1. Summary
Did stuff.

## 6. Unresolved Issues & Next Steps
- The `zorp` module is failing on import. We need to investigate the `zorp.py` file.
- Another unrelated issue.
"""
    (project_root / "handoffs" / "20251010.md").write_text(handoff_content)

    scratch_content = "import zorp\n\n# I think the problem is with the zorp import statement."
    (project_root / "scratch" / "zorp_import_fix_idea.py").write_text(scratch_content)

    # 2. Act: Run the script
    excavate_scratch.main()

    # 3. Assert: Check the output
    captured = capsys.readouterr()
    assert "[!] Potential Match Found!" in captured.out
    assert "The `zorp` module is failing on import" in captured.out
    assert "scratch/zorp_import_fix_idea.py" in captured.out
    assert "zorp, import" in captured.out or "import, zorp" in captured.out # Keywords

def test_excavate_scratch_no_match(setup_excavation_test_env, capsys):
    """
    Tests that the script reports no matches when keywords don't overlap.
    """
    project_root = setup_excavation_test_env

    # 1. Arrange: Create non-matching test data
    handoff_content = """
## 6. Unresolved Issues & Next Steps
- The database connection is timing out.
"""
    (project_root / "handoffs" / "20251011.md").write_text(handoff_content)
    (project_root / "scratch" / "some_unrelated_script.js").write_text("console.log('hello');")

    # 2. Act: Run the script
    excavate_scratch.main()

    # 3. Assert: Check the output
    captured = capsys.readouterr()
    assert "[!] Potential Match Found!" not in captured.out
    assert "No correlations found" in captured.out
