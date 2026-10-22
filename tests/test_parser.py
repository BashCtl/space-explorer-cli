from datetime import datetime
from unittest import result
from unittest.mock import MagicMock

import pytest

from space.errors import ApiValueError, SpaceTypeError
from space.models import NEOResponse
from space.parser import (
    compute_neo_range,
    parse_apod_date,
    parse_neo_date,
    parse_neo_feed,
)


@pytest.fixture()
def mock_datetime(monkeypatch):
    fixed_now = datetime(2026, 1, 15, 10, 30, 0)

    mock_dt = MagicMock()
    mock_dt.now.return_value = fixed_now
    mock_dt.strftime = datetime.strftime
    mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    mock_dt.strptime = datetime.strptime

    monkeypatch.setattr("space.parser.datetime", mock_dt)

    return fixed_now


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


def test_parse_apod_date_rejects_datetime_string():
    with pytest.raises(ApiValueError):
        parse_apod_date("2025-01-01T12:30:00")


def test_parse_apod_date_rejects_non_string():
    with pytest.raises((TypeError, ApiValueError)):
        parse_apod_date(None)


@pytest.mark.parametrize(
    ("days", "expected_start", "expected_end"),
    [
        (0, "2026-01-15", "2026-01-15"),
        (1, "2026-01-15", "2026-01-16"),
        (3, "2026-01-15", "2026-01-18"),
        (7, "2026-01-15", "2026-01-22"),
    ],
)
def test_compute_neo_range_valid_days(
    mock_datetime, days, expected_start, expected_end
):
    result = compute_neo_range(days)

    assert result == (expected_start, expected_end)


def test_compute_neo_range_zero_days(mock_datetime):
    start_date, end_date = compute_neo_range(0)

    assert start_date == "2026-01-15"
    assert end_date == start_date


def test_compute_neo_range_maximum_days(mock_datetime):
    start_date, end_date = compute_neo_range(7)

    assert start_date == "2026-01-15"
    assert end_date == "2026-01-22"


@pytest.mark.parametrize("days", [8, 10, 30, 365])
def test_compute_neo_range_rejects_more_than_seven_days(days):
    with pytest.raises(
        ApiValueError,
        match="Days ahead parameter can not be bigger than 7.",
    ):
        compute_neo_range(days)


@pytest.mark.parametrize("days", [-1, -5, -100])
def test_compute_neo_range_rejects_negative_days(days):
    with pytest.raises(
        ApiValueError,
        match="Days ahead parameter must be a postive integer",
    ):
        compute_neo_range(days)


@pytest.mark.parametrize(
    "days",
    ["3", None, [], {}, object()],
)
def test_compute_neo_range_rejects_invalid_types(days):
    with pytest.raises(SpaceTypeError) as exc_info:
        compute_neo_range(days)

    assert str(exc_info.value) == "Days param must be and integer number."
    assert isinstance(exc_info.value.__cause__, TypeError)


def test_parse_neo_feed_sorts_by_miss_distance(neo_response):
    result = parse_neo_feed(neo_response)
    assert (
        result[0].close_approach_data[0].miss_distance.kilometers
        < result[1].close_approach_data[0].miss_distance.kilometers
    )


def test_parse_neo_feed_filters_hazardous_asteroids(neo_response):
    result = parse_neo_feed(neo_response, hazardous=True)

    assert all(a.is_potentially_hazardous_asteroid for a in result)


def test_parse_neo_feed_applies_default_limit_of_ten(neo_response):
    result = parse_neo_feed(neo_response)
    assert len(result) == 10


@pytest.mark.parametrize("limit", [0, 1, 3, 5])
def test_parse_neo_feed_respects_custom_limit(neo_response, limit):
    result = parse_neo_feed(neo_response, limit=limit)
    assert len(result) == limit
