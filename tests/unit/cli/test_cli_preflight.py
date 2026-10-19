"""Unit tests for SACL V1 CLI preflight command."""

from __future__ import annotations

import shutil
from unittest.mock import MagicMock, patch
import pytest

from sacl.cli.main import main


def test_cli_preflight_clean(tmp_path, capsys, monkeypatch):
    # Simulate availability of the mandatory Windows host dependency on POSIX CI.
    # The real preflight continues to fail closed when PowerShell is absent.
    original_which = shutil.which
    monkeypatch.setattr(
        "sacl.cli.preflight.shutil.which",
        lambda command: "mock-powershell" if command == "powershell.exe" else original_which(command),
    )
    code = main(["preflight", "--repo", str(tmp_path)])
    assert code == 0
    captured = capsys.readouterr()
    assert "SACL PREFLIGHT ENVIRONMENT CHECK" in captured.out
    assert "PREFLIGHT VERDICT: PASS" in captured.out


def test_cli_preflight_dirty_root(tmp_path, capsys):
    (tmp_path / ".git").mkdir()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=" M dirty_file.py\n")
        code = main(["preflight", "--repo", str(tmp_path)])
        assert code == 1
        captured = capsys.readouterr()
        assert "Local Dirty-Root Rule Violation" in captured.out
        assert "PREFLIGHT VERDICT: FAIL" in captured.out


def test_cli_preflight_missing_mandatory_powershell_fails(capsys, monkeypatch):
    original_which = shutil.which
    monkeypatch.setattr(
        "sacl.cli.preflight.shutil.which",
        lambda command: None if command in ("powershell.exe", "powershell") else original_which(command),
    )
    assert main(["preflight"]) == 1
    assert "PREFLIGHT VERDICT: FAIL" in capsys.readouterr().out
