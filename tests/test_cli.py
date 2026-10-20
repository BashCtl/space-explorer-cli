from typer.testing import CliRunner

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
