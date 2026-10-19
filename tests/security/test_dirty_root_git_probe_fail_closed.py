"""T56: Git status probe failures must not bypass the dirty-root gate."""

from __future__ import annotations

from argparse import Namespace
from types import SimpleNamespace
from unittest.mock import Mock
import shutil
import subprocess

import pytest

from sacl.cli.preflight import execute_preflight
from sacl.contracts.exceptions import DirtyRootError
from sacl.legacy.compatibility import check_dirty_root
from sacl.legacy.operator import LegacyOperatorExperience


@pytest.fixture
def git_checkout(tmp_path):
    (tmp_path / ".git").mkdir()
    return tmp_path


@pytest.mark.parametrize(
    "failure",
    [
        subprocess.CalledProcessError(128, ["git", "status"]),
        subprocess.TimeoutExpired(["git", "status"], 15),
        FileNotFoundError("git executable missing"),
        PermissionError("git execution denied"),
    ],
    ids=["git-exit-128", "git-timeout", "git-missing", "git-permission"],
)
def test_git_probe_failure_is_not_clean(git_checkout, monkeypatch, failure):
    monkeypatch.setattr("sacl.legacy.compatibility.subprocess.run", Mock(side_effect=failure))
    is_dirty, details = check_dirty_root(git_checkout)
    assert is_dirty is True
    assert details.startswith("GIT_CHECK_ERROR:")


@pytest.mark.parametrize(
    "porcelain, expected",
    [("", False), (" M tracked.py\n", True), ("?? new.py\n", True)],
)
def test_git_probe_known_state_preserved(git_checkout, monkeypatch, porcelain, expected):
    monkeypatch.setattr(
        "sacl.legacy.compatibility.subprocess.run",
        Mock(return_value=Mock(stdout=porcelain)),
    )
    is_dirty, details = check_dirty_root(git_checkout)
    assert is_dirty is expected
    assert details == porcelain.strip()


def test_preflight_refuses_git_probe_error(git_checkout, monkeypatch, capsys):
    original_which = shutil.which
    monkeypatch.setattr(
        "sacl.cli.preflight.shutil.which",
        lambda command: "mock-powershell" if command == "powershell.exe" else original_which(command),
    )
    monkeypatch.setattr(
        "sacl.legacy.compatibility.subprocess.run",
        Mock(side_effect=subprocess.CalledProcessError(128, ["git", "status"])),
    )
    assert execute_preflight(Namespace(repo=str(git_checkout), db=None)) == 1
    assert "PREFLIGHT VERDICT: FAIL" in capsys.readouterr().out


def test_legacy_operator_refuses_git_probe_error_before_worker(git_checkout, monkeypatch):
    operator = LegacyOperatorExperience()
    operator.adapter.load_manifest = Mock(
        return_value=SimpleNamespace(
            target_local_repo=str(git_checkout), source_orchestrator=str(git_checkout)
        )
    )
    monkeypatch.setattr(
        "sacl.legacy.compatibility.subprocess.run",
        Mock(side_effect=subprocess.TimeoutExpired(["git", "status"], 15)),
    )
    with pytest.raises(DirtyRootError):
        operator.run_wave(
            package_path=git_checkout,
            repo_path=git_checkout,
            bypass_acknowledged=True,
            test_mode=False,
        )
    assert not (git_checkout / "runs").exists()
