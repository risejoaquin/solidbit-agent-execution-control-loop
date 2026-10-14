"""Generate explicit CI-only evidence; never claim real-host or legacy parity certification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


STEPS = {
    "TEST-01-AST": "Windows PowerShell AST parser",
    "TEST-02-SCHEMA": "Versioned manifest schema and required job_id",
    "TEST-03-SANDBOX": "Disposable local Git bare remote and clone",
    "TEST-04-DIRTY": "Worktree isolation, dirty-root and branch guards",
    "TEST-05-LOCKS": "SQLite WAL, 16 domains and lease exclusion",
    "TEST-06-RECON": "Three-factor process identity and PID recycling",
    "TEST-07-STOP": "Safe-stop and non-killing diagnostic timeout",
    "TEST-08-GATE": "Regex fallback and collision integration gate",
}


def build_report(junit: Path, runner: str, ast_marker: Path) -> dict:
    observed: dict[str, str] = {}
    if junit.exists():
        root = ET.parse(junit).getroot()
        for case in root.iter("testcase"):
            name = case.attrib.get("name", "")
            for number in range(2, 9):
                if name.startswith(f"test_{number:02d}_"):
                    observed[f"TEST-{number:02d}"] = (
                        "FAIL" if case.find("failure") is not None or case.find("error") is not None
                        else "SKIPPED" if case.find("skipped") is not None
                        else "PASS"
                    )
    lines = []
    for index, (key, label) in enumerate(STEPS.items(), start=1):
        if index == 1:
            status = "PASS" if runner == "Windows" and ast_marker.exists() else "NOT_RUN"
        else:
            status = observed.get(f"TEST-{index:02d}", "NOT_RUN")
        lines.append({"id": key, "name": label, "status": status})

    # Strictly distinguish CI mock validation from operational certification.
    mock_pass = all(e["status"] == "PASS" for e in lines[1:])
    ast_pass = lines[0]["status"] == "PASS"
    return {
        "schema": "solidbit.ci-mock-e2e-evidence.v1",
        "runner": runner,
        "mock_steps_02_08": "PASS" if mock_pass else "INCOMPLETE_OR_FAILED",
        "step_01_ast": "PASS" if ast_pass else "NOT_VERIFIED_ON_THIS_RUNNER",
        "overall_ci_rehearsal": "PASS" if mock_pass and ast_pass else "PARTIAL_OR_FAILED",
        "legacy_18_capability_parity": "NOT_VERIFIED",
        "host_real_process_certification": "NOT_PERFORMED",
        "operational_authorization": "NOT_GRANTED",
        "steps": lines,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", type=Path, required=True)
    parser.add_argument("--runner", choices=("Windows", "Linux"), required=True)
    parser.add_argument("--ast-marker", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(args.junit, args.runner, args.ast_marker)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "E2E_MOCK_EVIDENCE.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# SACL — Mock E2E CI evidence", "",
        f"Runner: {report['runner']}",
        f"CI rehearsal: **{report['overall_ci_rehearsal']}**", "",
        "| Gate | Scope | Result |", "|---|---|---|",
    ]
    lines += [
        f"| {entry['id']} | {entry['name']} | {entry['status']} |"
        for entry in report["steps"]
    ]
    lines += [
        "", "**Production authorization: NOT GRANTED.**",
        "**Historical orchestrator 18/18 parity: NOT VERIFIED.**",
        "**Real Windows host worker certification: NOT PERFORMED.**",
        "Tests use a disposable local Git remote and mocks; no real agents, secrets or cloud services.",
        "",
    ]
    md = "\n".join(lines)
    (args.output_dir / "E2E_MOCK_EVIDENCE.md").write_text(md, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
