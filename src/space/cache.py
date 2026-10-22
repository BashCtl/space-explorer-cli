import json
import os
import tempfile
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
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise SpaceJSONDecodeError("Invalid cache JSON file") from exc

    if not isinstance(data, dict):
        raise SpaceJSONDecodeError("Cache JSON root must be an object")
    return data


def save_cache(response_json, **params) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        data = load_all_cache()
    except SpaceJSONDecodeError:
        data = {}

    data[_cache_key(params)] = {
        "created_at": datetime.now(UTC).isoformat(),
        "data": response_json,
    }

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=CACHE_FILE.parent,
            prefix=f".{CACHE_FILE.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_path, CACHE_FILE)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def load_cache(ttl, **params) -> dict[Any, Any]:
    try:
        data = load_all_cache()
    except SpaceJSONDecodeError:
        return {}

    cached_response = data.get(_cache_key(params))
    if not isinstance(cached_response, dict):
        return {}

    created_at = cached_response.get("created_at")
    if not isinstance(created_at, str) or "data" not in cached_response:
        return {}
    try:
        if not is_cache_valid(created_at, ttl):
            return {}
    except ApiValueError:
        return {}
    return cached_response["data"]


def is_cache_valid(created_at, ttl):
    try:
        timestamp = datetime.fromisoformat(created_at)
        age = datetime.now(UTC) - timestamp
        return timedelta(0) <= age < ttl
    except (TypeError, ValueError) as exc:
        raise ApiValueError("Invalid 'created_at' timestamp") from exc
