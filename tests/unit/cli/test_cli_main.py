"""Unit tests for SACL V1 CLI Main parser and entrypoint."""

from __future__ import annotations

import pytest

from sacl.cli.main import build_parser, main


def test_cli_version(capsys):
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "SACL V1 CLI Version" in captured.out


def test_cli_help(capsys):
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "launch" in captured.out
    assert "status" in captured.out
    assert "stop" in captured.out
    assert "monitor" in captured.out
    assert "package" in captured.out
    assert "preflight" in captured.out


def test_cli_missing_command(capsys):
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code != 0
