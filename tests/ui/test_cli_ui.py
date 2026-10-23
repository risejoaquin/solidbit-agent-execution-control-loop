"""Unit tests for SACL V1 CLI UI subcommand."""

from sacl.cli.main import build_parser


def test_cli_ui_parser():
    parser = build_parser()
    args = parser.parse_args(["ui", "--host", "0.0.0.0", "--port", "9000", "--no-browser"])
    assert args.subcommand == "ui"
    assert args.host == "0.0.0.0"
    assert args.port == 9000
    assert args.no_browser is True


def test_cli_dashboard_alias_parser():
    parser = build_parser()
    args = parser.parse_args(["dashboard", "--port", "8888"])
    assert args.subcommand == "dashboard"
    assert args.port == 8888
