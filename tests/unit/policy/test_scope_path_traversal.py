"""P0: bounded approvals reject traversal and ambiguous Windows paths (mock-only)."""
import pytest
from sacl.policy.approval import matches_scope_pattern, is_scope_covered

@pytest.mark.parametrize("requested", [
    "docs/../src/secrets.py", "docs/../../main", "docs\\..\\secret",
    "docs/./a.md", "docs//a.md", "docs/", "/docs/a.md",
    "C:/docs/a.md", "C:docs/a.md", "\\\\server\\share\\docs\\a.md",
    "docs/a.md\x00.txt",
])
def test_reject_unsafe_target_even_when_glob_matches(requested):
    assert not matches_scope_pattern("docs/*", requested)
    assert not matches_scope_pattern("*", requested)
    assert not is_scope_covered(["docs/*", "*"], [requested])

@pytest.mark.parametrize("pattern", [
    "docs/../*", "docs\\..\\*", "docs//**", "/docs/*",
    "C:/docs/*", "\\\\server\\share\\*", "docs/./*", "docs/",
])
def test_reject_unsafe_approval_pattern(pattern):
    assert not matches_scope_pattern(pattern, "docs/a.md")

@pytest.mark.parametrize("pattern,target", [
    ("docs/*", "docs/ARCHITECTURE.md"),
    ("docs/*", "docs/adr/ADR-001.md"),
    ("schemas/*", "schemas/approval.schema.json"),
    ("feature/*", "feature/task-1"),
    ("docs/*", "docs\\sub\\file.md"),
    ("*", "anything.txt"),
    ("**", "docs/sub/file.md"),
    ("docs", "docs/a.md"),
])
def test_existing_relative_scope_contract_preserved(pattern, target):
    assert matches_scope_pattern(pattern, target)

def test_multi_scope_and_out_of_scope():
    assert is_scope_covered(["docs/*", "schemas/*"], ["docs/a.md", "schemas/b.json"])
    assert not is_scope_covered(["docs/*"], ["docs/a.md", "src/b.py"])

@pytest.mark.parametrize("requested", [
    "docs/report.md:payload", "docs/report.md.", "docs/report.md ",
    "docs/NUL.txt", "docs/con", "docs/COM1.log", "docs/LPT9",
    "docs/CONIN$", "docs/CONOUT$", "docs/aux.json", "docs\\..//a",
    "docs/a.md/..", "docs/a.md/.", " docs/a.md", "docs/a.md ",
])
def test_windows_aliases_cannot_escape_approval_scope(requested):
    assert not matches_scope_pattern("*", requested)
    assert not is_scope_covered(["*"], [requested])

@pytest.mark.parametrize("pattern", [
    "docs/*:stream", "docs/COM1", "docs/NUL.txt", "docs/ ",
    "docs/file.", "docs/file ", "docs\\..\\*",
])
def test_unsafe_approval_patterns_cannot_grant_access(pattern):
    assert not matches_scope_pattern(pattern, "docs/file.md")

@pytest.mark.parametrize("invalid", [None, 0, [], {}, "", "\x00"])
def test_malformed_scope_references_fail_closed(invalid):
    assert not matches_scope_pattern("*", invalid)
    assert not matches_scope_pattern(invalid, "docs/a.md")

@pytest.mark.parametrize("target", [
    "docs/file?.md", "docs/file*.md", "docs/file[0].md",
    "docs/a<report>.md", "docs/a>report.md", "docs/a|report.md",
    'docs/a"report.md', "docs/a\x01.md", "docs/a\x7f.md",
])
def test_invalid_windows_filename_or_glob_target_is_not_authorized(target):
    assert not matches_scope_pattern("*", target)
    assert not is_scope_covered(["*"], [target])

@pytest.mark.parametrize("pattern", [
    "docs/a<report>.md", "docs/a>report.md", "docs/a|report.md",
    'docs/a"report.md', "docs/a\x02.md", "docs/a\x7f.md",
])
def test_invalid_pattern_character_cannot_grant_access(pattern):
    assert not matches_scope_pattern(pattern, "docs/a.md")

@pytest.mark.parametrize("pattern,target", [
    ("docs/file?.md", "docs/file1.md"),
    ("docs/file[0-9].md", "docs/file5.md"),
    ("docs/*.md", "docs/notes.md"),
])
def test_glob_metacharacters_remain_legal_in_patterns(pattern, target):
    assert matches_scope_pattern(pattern, target)
