from unittest.mock import MagicMock, call, patch

import pytest
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from space.formatter import Formatter


@pytest.fixture
def formatter():
    with patch("space.formatter.Console") as mock_console:
        instance = Formatter()
        instance.console = MagicMock()
        instance.err_console = MagicMock()
        yield instance


def make_apod(
    title="Test APOD",
    date="2026-01-01",
    explanation="Explanation: A beautiful image of space.",
    permalink="https://example.com/apod",
    media_type="image",
    hdurl="https://example.com/image.jpg",
):
    apod = MagicMock()
    apod.title = title
    apod.date = date
    apod.explanation = explanation
    apod.permalink = permalink
    apod.media_type = media_type
    apod.hdurl = hdurl
    return apod


def make_asteroid(
    name="Test Asteroid",
    close_approach_date="2026-01-01",
    velocity=25000.123,
    miss_distance_km=100000.25,
    miss_distance_lunar=2.5,
    diameter_max=1.234,
    hazardous=False,
):
    asteroid = MagicMock()
    asteroid.name = name

    approach = MagicMock()
    approach.close_approach_date = close_approach_date
    approach.relative_velocity.kilometers_per_hour = velocity
    approach.miss_distance.kilometers = miss_distance_km
    approach.miss_distance.lunar = miss_distance_lunar

    asteroid.close_approach_data = [approach]
    asteroid.estimated_diameter.kilometers.estimated_diameter_max = diameter_max
    asteroid.is_potentially_hazardous_asteroid = hazardous

    return asteroid


def test_print_apods_with_image(formatter):
    apod = make_apod()

    formatter.print_apods([apod])

    assert formatter.console.print.call_count >= 4

    formatter.console.rule.assert_any_call(
        "[bold green]Test APOD[/bold green]",
        align="left",
        style="bold cyan",
    )

    formatter.console.print.assert_any_call(
        "[bold][cyan]Date:[/cyan] [green]2026-01-01[/green][/bold]"
    )

    formatter.console.print.assert_any_call(
        "[cyan bold]Post link: [/cyan bold]",
        "[link=https://example.com/apod underline blue]"
        "https://example.com/apod[/link]\n",
    )

    formatter.console.print.assert_any_call(
        "[cyan bold]Image link: [/cyan bold]",
        "[link=https://example.com/image.jpg underline blue]Test APOD[/link]",
    )

    formatter.console.rule.assert_any_call(style="bold cyan")


def test_print_apods_removes_explanation_prefix(formatter):
    apod = make_apod(explanation="Explanation: This is a test explanation.")

    formatter.print_apods([apod])

    printed_panel = next(
        call_args.args[0]
        for call_args in formatter.console.print.call_args_list
        if call_args.args and isinstance(call_args.args[0], Panel)
    )

    assert str(printed_panel.renderable) == "This is a test explanation."


def test_print_apods_with_empty_list(formatter):
    formatter.print_apods([])

    formatter.console.rule.assert_called_once_with(style="bold cyan")
    formatter.console.print.assert_not_called()


def test_print_apods_video(formatter):
    apod = make_apod(media_type="video")

    formatter.print_apods([apod])

    formatter.console.print.assert_any_call(
        "[cyan bold]Video can be find by link: [/cyan bold]",
        "[link=https://example.com/apod underline blue]"
        "https://example.com/apod[/link ]",
    )


def test_print_asteroids_table_prints_table(formatter):
    asteroid = make_asteroid()

    formatter.print_asteroids_table([asteroid])

    formatter.console.print.assert_called_once()

    table = formatter.console.print.call_args.args[0]
    assert isinstance(table, Table)
    assert table.title == "Asteroids"


def test_print_asteroids_table_has_expected_columns(formatter):
    formatter.print_asteroids_table([])

    table = formatter.console.print.call_args.args[0]

    assert [column.header for column in table.columns] == [
        "Name",
        "Close Approach Date",
        "Relative Velocity km/h",
        "Miss Distance km",
        "Miss Distance Lunar",
        "Max Diameter km",
        "Potentially Hazardous",
    ]


def test_print_asteroids_table_formats_asteroid_values(formatter):
    asteroid = make_asteroid(
        name="2026 AB",
        close_approach_date="2026-01-10",
        velocity=25000.123,
        miss_distance_km=123456.78,
        miss_distance_lunar=3.6,
        diameter_max=1.234,
        hazardous=False,
    )

    formatter.print_asteroids_table([asteroid])

    table = formatter.console.print.call_args.args[0]

    assert len(table.rows) == 1

    values = [column._cells[0] for column in table.columns]

    assert values == [
        "2026 AB",
        "2026-01-10",
        "25,000.12",
        "123,456.8",
        "4",
        "1.23",
        "NO",
    ]


def test_print_asteroids_table_marks_hazardous_asteroid(formatter):
    asteroid = make_asteroid(hazardous=True)

    formatter.print_asteroids_table([asteroid])

    table = formatter.console.print.call_args.args[0]
    hazardous_cell = table.columns[-1]._cells[-1]

    assert hazardous_cell == "[red]YES[/red]"


def test_print_asteroids_table_with_empty_list(formatter):
    formatter.print_asteroids_table([])

    formatter.console.print.assert_called_once()

    table = formatter.console.print.call_args.args[0]

    assert isinstance(table, Table)
    assert len(table.rows) == 0


def test_print_raw_json_calls_console_print_json(formatter):
    json_data = {"name": "Earth", "moons": 1}

    formatter.print_raw_json(json_data)

    formatter.console.print_json.assert_called_once_with(
        data=json_data,
        indent=4,
    )


def test_print_raw_json_handles_empty_dict(formatter):
    formatter.print_raw_json({})

    formatter.console.print_json.assert_called_once_with(
        data={},
        indent=4,
    )


def test_print_error_calls_error_console(formatter):
    exception = ValueError("Something went wrong")

    formatter.print_error(exception)

    formatter.err_console.print.assert_called_once_with(
        "[red bold]Error: [/red bold] Something went wrong"
    )


def test_print_error_handles_custom_exception(formatter):
    exception = RuntimeError("API unavailable")

    formatter.print_error(exception)

    formatter.err_console.print.assert_called_once_with(
        "[red bold]Error: [/red bold] API unavailable"
    )
