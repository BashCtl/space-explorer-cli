from unittest.mock import MagicMock

from conftest import make_fake_apod_client
from typer.testing import CliRunner
from space.client import Endpoints
from space.cli import app

runner = CliRunner()


def invoke(*args):
    return runner.invoke(app, [*args])


def test_apod_help():
    result = invoke("apod", "--help")

    assert result.exit_code == 0
    assert "--date" in result.stdout
    assert "--recent" in result.stdout
    assert "--from" in result.stdout
    assert "--to" in result.stdout
    assert "--timeout" in result.stdout
    assert "--raw" in result.stdout


def test_asteroids_help():
    result = invoke("asteroids", "--help")

    assert result.exit_code == 0
    assert "--days" in result.stdout
    assert "--start" in result.stdout
    assert "--end" in result.stdout
    assert "--hazardous-only" in result.stdout
    assert "--limit" in result.stdout
    assert "--timeout" in result.stdout
    assert "--plot" in result.stdout


def test_missing_arguments():
    result = invoke("")
    assert result.exit_code == 2
    assert " No such command ''. " in result.stderr


def test_apod_command_parses_args_to_client(monkeypatch, apod_res):
    fake_client = make_fake_apod_client(monkeypatch, response=apod_res)
    fake_formatter = MagicMock()
    fake_apod = MagicMock()
    monkeypatch.setattr("space.cli.Formatter", lambda: fake_formatter)
    monkeypatch.setattr("space.cli.Apod", fake_apod)
    result = invoke("apod", "--from", "2026-10-14", "--to", "2026-10-15")

    assert result.exit_code == 0, result.output
    fake_client.get_apods.assert_called_once()

    args, kwargs = fake_client.get_apods.call_args
    assert args[0] == Endpoints.APOD_BASIC
    assert kwargs["date_from"] == "261014"
    assert kwargs["date_to"] == "261015"
    assert kwargs["timeout"] == 10

    fake_apod.parse_json.assert_called_once_with(apod_res)
    fake_formatter.print_apods.assert_called_once()
