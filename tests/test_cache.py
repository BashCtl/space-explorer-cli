import json
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, mock_open, patch

import pytest

from space import cache
from space.errors import ApiValueError, SpaceJSONDecodeError


def test_cache_key_serializes_params():
    params = {"date": "2026-01-01", "count": 5}
    result = cache._cache_key(params)
    assert result == json.dumps(params, ensure_ascii=False)


def test_cache_key_is_deterministic():
    params = {"a": 1, "b": 2}

    assert cache._cache_key(params) == cache._cache_key(params)


def test_load_all_cache_returns_empty_dict_when_file_missing(cache_file):
    assert cache.load_all_cache() == {}


def test_load_all_cache_reads_json(cache_file):
    expected = {"key": {"data": {"value": 43}}}
    cache_file.write_text(json.dumps(expected), encoding="utf-8")

    result = cache.load_all_cache()

    assert result == expected


def test_load_all_cache_propagates_invalid_json(cache_file):
    cache_file.write_text("{invalid json", encoding="utf-8")
    with pytest.raises(SpaceJSONDecodeError):
        cache.load_all_cache()


def test_save_cache_creates_directory_and_save_data(cache_file):
    response = {"title": "Astronomy Picture of the Day"}

    cache.save_cache(response, date="2026-01-01")

    assert cache_file.exists()

    saved = json.loads(cache_file.read_text(encoding="utf-8"))
    key = cache._cache_key({"date": "2026-01-01"})

    assert key in saved
    assert saved[key]["data"] == response
    assert "created_at" in saved[key]

    created_at = datetime.fromisoformat(saved[key]["created_at"])
    assert created_at.tzinfo == UTC


def test_case_cache_preserves_existing_entries(cache_file):
    existing = {
        "existing-key": {
            "created_at": datetime.now(UTC).isoformat(),
            "data": {"old": True},
        }
    }

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(existing), encoding="utf-8")

    cache.save_cache({"new": True}, date="2026-10-10")

    saved = json.loads(cache_file.read_text(encoding="utf-8"))

    assert saved["existing-key"] == existing["existing-key"]
    assert saved[cache._cache_key({"date": "2026-10-10"})]["data"] == {"new": True}


def test_is_cache_valid_when_timestamp_is_recent(monkeypatch):
    now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    monkeypatch.setattr(cache, "datetime", MagicMock())
    cache.datetime.now.return_value = now  # type: ignore
    cache.datetime.fromisoformat = datetime.fromisoformat

    created_at = (now - timedelta(hours=1)).isoformat()

    assert cache.is_cache_valid(created_at, timedelta(hours=12)) is True


def test_is_cache_valid_when_timestamp_is_expired(monkeypatch):
    now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    monkeypatch.setattr(cache, "datetime", MagicMock())
    cache.datetime.now.return_value = now  # type: ignore
    cache.datetime.fromisoformat = datetime.fromisoformat

    created_at = (now - timedelta(hours=13)).isoformat()

    assert cache.is_cache_valid(created_at, timedelta(hours=12)) is False


def test_is_cache_valid_at_exact_ttl_boundary(monkeypatch):
    now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    monkeypatch.setattr(cache, "datetime", MagicMock())
    cache.datetime.now.return_value = now  # type: ignore
    cache.datetime.fromisoformat = datetime.fromisoformat

    created_at = (now - timedelta(hours=12)).isoformat()

    assert cache.is_cache_valid(created_at, timedelta(hours=12)) is False


def test_is_cache_valid_propagates_invalid_timestamp():
    with pytest.raises(ApiValueError):
        cache.is_cache_valid("not-a-timestamp", timedelta(hours=1))


def test_load_cache_returns_empty_dict_when_key_missing(monkeypatch):
    monkeypatch.setattr(cache, "load_all_cache", MagicMock(return_value={}))
    assert cache.load_cache(timedelta(hours=12), date="2026-01-01") == {}


def test_load_cache_returns_empty_dict_when_expired(monkeypatch):
    cached = {
        cache._cache_key({"date": "2026-01-01"}): {
            "created_at": "2020-01-01T00:00:00+00:00",
            "data": {"value": 42},
        }
    }

    monkeypatch.setattr(cache, "load_all_cache", MagicMock(return_value=cached))
    monkeypatch.setattr(cache, "is_cache_valid", MagicMock(return_value=False))

    result = cache.load_cache(timedelta(hours=12), date="2026-01-01")

    assert result == {}

    cache.is_cache_valid.assert_called_once_with(  # type: ignore
        "2020-01-01T00:00:00+00:00",
        timedelta(hours=12),
    )


def test_load_cache_returns_data_when_valid(monkeypatch):
    params = {"date": "2026-01-01"}
    response = {"title": "APOD"}
    created_at = "2026-01-01T11:00:00+00:00"

    cached = {
        cache._cache_key(params): {
            "created_at": created_at,
            "data": response,
        }
    }
    monkeypatch.setattr(cache, "load_all_cache", MagicMock(return_value=cached))
    monkeypatch.setattr(cache, "is_cache_valid", MagicMock(return_value=True))

    result = cache.load_cache(timedelta(hours=12), **params)

    assert result == response
