"""Ensure summary generator is conservative if tests were missing or failed."""
from pathlib import Path
from scripts.report_e2e_mock import build_report


def test_no_junit_never_reports_certified(tmp_path: Path) -> None:
    report = build_report(tmp_path / "not-created.xml", "Windows", tmp_path / "absent")
    assert report["overall_ci_rehearsal"] == "PARTIAL_OR_FAILED"
    assert report["legacy_18_capability_parity"] == "NOT_VERIFIED"
    assert all(step["status"] == "NOT_RUN" for step in report["steps"])


def test_missing_steps_never_promoted_to_pass(tmp_path: Path) -> None:
    junit = tmp_path / "limited.xml"
    junit.write_text(
        '<testsuite><testcase name="test_02_manifest_schema_is_fail_closed"/></testsuite>',
        encoding="utf-8",
    )
    report = build_report(junit, "Linux", tmp_path / "not-here")
    assert report["steps"][1]["status"] == "PASS"
    assert report["steps"][2]["status"] == "NOT_RUN"
    assert report["overall_ci_rehearsal"] == "PARTIAL_OR_FAILED"
