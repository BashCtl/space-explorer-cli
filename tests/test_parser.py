import pytest

from space.errors import ApiValueError
from space.parser import parse_apod_date, parse_neo_date


def test_parse_valid_neo_cli_date():
    result = parse_neo_date("2026-10-20")
    assert str(result) == "2026-10-20"


def test_parse_invalid_neo_cli_date():
    with pytest.raises(
        ApiValueError, match="Invalid date format. Must be 'YYYY-MM-DD'."
    ):
        parse_neo_date("22222-22-10")


def test_parse_empy_neo_cli_date():
    with pytest.raises(
        ApiValueError, match="Invalid date format. Must be 'YYYY-MM-DD'."
    ):
        parse_neo_date("")


def test_parse_valid_apod_date():
    result = parse_apod_date("2026-10-20")
    assert result == "261020"


def test_parse_invalid_apod_date():
    with pytest.raises(
        ApiValueError, match="Invalid date '2026-19-10'. Expected format: YYYY-MM-DD"
    ):
        parse_apod_date("2026-19-10")


def test_parse_empty_apod_date():
    with pytest.raises(
        ApiValueError, match="Invalid date ''. Expected format: YYYY-MM-DD"
    ):
        parse_apod_date("")
