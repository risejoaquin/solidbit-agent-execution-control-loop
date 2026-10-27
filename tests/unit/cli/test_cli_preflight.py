"""Unit tests for SACL V1 CLI preflight command."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from sacl.cli.main import main


def test_cli_preflight_clean(tmp_path, capsys):
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
