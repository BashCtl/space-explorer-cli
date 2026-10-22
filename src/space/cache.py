import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from space.errors import ApiValueError, SpaceJSONDecodeError

CACHE_FILE = Path(".cache/data.json")
APOD_TTL = timedelta(hours=12)
NEO_TTL = timedelta(hours=6)


def _cache_key(params: dict) -> str:
    return json.dumps(params, ensure_ascii=False)


def load_all_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}

    try:
        with CACHE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise SpaceJSONDecodeError("Invalid json file") from exc


def save_cache(response_json, **params) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = load_all_cache()
    data[_cache_key(params)] = {
        "created_at": datetime.now(UTC).isoformat(),
        "data": response_json,
    }

    with CACHE_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def load_cache(ttl, **params) -> dict[Any, Any]:
    data = load_all_cache()
    cached_response = data.get(_cache_key(params), {})
    if not cached_response:
        return {}
    created_at = cached_response["created_at"]
    if not is_cache_valid(created_at, ttl):
        return {}
    return cached_response.get("data")


def is_cache_valid(created_at, ttl):
    try:
        timestamp = datetime.fromisoformat(created_at)
        age = datetime.now(UTC) - timestamp
        return age < ttl
    except ValueError as exc:
        raise ApiValueError("Invalid 'created_at' timestamp") from exc
