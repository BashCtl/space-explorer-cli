from unittest.mock import MagicMock

from conftest import make_fake_apod_client, make_fake_asteroids_client
from typer.testing import CliRunner

from space.cli import app
from space.client import Endpoints

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


def test_apod_command_parses_args_to_client(monkeypatch, apod_res, cache_file):
    fake_client = make_fake_apod_client(monkeypatch, response=apod_res)
    fake_formatter = MagicMock()
    fake_apod = MagicMock()
    fake_load_cache = MagicMock()
    monkeypatch.setattr("space.cli.Formatter", lambda: fake_formatter)
    monkeypatch.setattr("space.cli.Apod", fake_apod)
    monkeypatch.setattr("space.cli.load_cache", fake_load_cache)
    result = invoke("apod", "--from", "2026-10-14", "--to", "2026-10-15", "--no-cache")

    assert result.exit_code == 0, result.output
    fake_client.get_apods.assert_called_once()

    args, kwargs = fake_client.get_apods.call_args
    assert args[0] == Endpoints.APOD_BASIC
    assert kwargs["date_from"] == "261014"
    assert kwargs["date_to"] == "261015"
    assert kwargs["timeout"] == 10

    fake_apod.parse_json.assert_called_once_with(apod_res)
    fake_formatter.print_apods.assert_called_once()
    fake_load_cache.assert_not_called()


def test_asteroids_command_parses_args_to_client(
    monkeypatch, asteroids_res, cache_file
):
    fake_client = make_fake_asteroids_client(monkeypatch, response=asteroids_res)
    fake_formatter = MagicMock()
    fake_neo = MagicMock()
    fake_load_cache = MagicMock()

    monkeypatch.setattr("space.cli.Formatter", lambda: fake_formatter)
    monkeypatch.setattr("space.cli.NEOResponse", fake_neo)
    monkeypatch.setattr("space.cli.load_cache", fake_load_cache)

    result = invoke(
        "asteroids",
        "--start",
        "2026-10-14",
        "--end",
        "2026-10-15",
        "--no-cache",
    )

    assert result.exit_code == 0, result.output
    fake_client.get_asteroids.assert_called_once_with(
        Endpoints.NEO_FEED,
        timeout=10,
        start_date="2026-10-14",
        end_date="2026-10-15",
    )

    fake_neo.parse_json.assert_called_once_with(asteroids_res)
    fake_formatter.print_asteroids_table.assert_called_once()
    fake_load_cache.assert_not_called()


def test_apod_uses_cached_response(monkeypatch, apod_res):
    cached = {"items": ["cached"]}
    fake_client = make_fake_apod_client(monkeypatch, response=apod_res)
    fake_formatter = MagicMock()
    fake_apod = MagicMock()
    fake_load_cache = MagicMock()
    fake_save_cache = MagicMock()
    fake_load_cache.return_value = cached
    monkeypatch.setattr("space.cli.Formatter", lambda: fake_formatter)
    monkeypatch.setattr("space.cli.Apod", fake_apod)
    monkeypatch.setattr("space.cli.load_cache", fake_load_cache)
    monkeypatch.setattr("space.cli.save_cache", fake_save_cache)

    result = invoke("apod")

    assert result.exit_code == 0
    fake_client.get_apods.assert_not_called()
    fake_save_cache.assert_not_called()


def test_apod_no_cache_forces_api_request(monkeypatch, apod_res):
    cached = {"items": ["cached"]}
    fake_client = make_fake_apod_client(monkeypatch, response=apod_res)
    fake_formatter = MagicMock()
    fake_apod = MagicMock()
    fake_load_cache = MagicMock()
    fake_save_cache = MagicMock()
    fake_load_cache.return_value = cached
    monkeypatch.setattr("space.cli.Formatter", lambda: fake_formatter)
    monkeypatch.setattr("space.cli.Apod", fake_apod)
    monkeypatch.setattr("space.cli.load_cache", fake_load_cache)
    monkeypatch.setattr("space.cli.save_cache", fake_save_cache)

    result = invoke("apod", "--no-cache")

    assert result.exit_code == 0
    fake_client.get_apods.assert_called_once()
    fake_save_cache.assert_called_once()
    fake_load_cache.assert_not_called()


def test_asteroids_uses_cached_response(monkeypatch, asteroids_res):
    cached = {"items": ["cached asteroid"]}
    fake_client = make_fake_asteroids_client(monkeypatch, response=asteroids_res)
    fake_formatter = MagicMock()
    fake_neo = MagicMock()
    fake_load_cache = MagicMock()
    fake_load_cache.return_value = cached
    fake_save_cache = MagicMock()
    monkeypatch.setattr("space.cli.Formatter", lambda: fake_formatter)
    monkeypatch.setattr("space.cli.NEOResponse", fake_neo)
    monkeypatch.setattr("space.cli.load_cache", fake_load_cache)
    monkeypatch.setattr("space.cli.save_cache", fake_save_cache)

    result = invoke("asteroids")

    assert result.exit_code == 0
    fake_client.get_asteroids.assert_not_called()
    fake_save_cache.assert_not_called()
    fake_load_cache.assert_called_once()


def test_asteroids_no_cache_forces_api_request(monkeypatch, asteroids_res):
    cached = {"items": ["cached asteroid"]}
    fake_client = make_fake_asteroids_client(monkeypatch, response=asteroids_res)
    fake_formatter = MagicMock()
    fake_neo = MagicMock()
    fake_load_cache = MagicMock()
    fake_load_cache.return_value = cached
    fake_save_cache = MagicMock()
    monkeypatch.setattr("space.cli.Formatter", lambda: fake_formatter)
    monkeypatch.setattr("space.cli.NEOResponse", fake_neo)
    monkeypatch.setattr("space.cli.load_cache", fake_load_cache)
    monkeypatch.setattr("space.cli.save_cache", fake_save_cache)

    result = invoke("asteroids", "--no-cache")

    assert result.exit_code == 0
    fake_client.get_asteroids.assert_called_once()
    fake_save_cache.assert_called_once()
    fake_load_cache.assert_not_called()
