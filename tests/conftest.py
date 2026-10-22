import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from space.models import NEOResponse

TEST_DATA = Path(__file__).parent / "data"


@pytest.fixture
def apod_res():
    with open(TEST_DATA / "apod_list.json") as file:
        return json.load(file)


@pytest.fixture
def asteroids_res():
    with open(TEST_DATA / "neo_feed.json") as file:
        return json.load(file)


@pytest.fixture
def neo_response(asteroids_res):
    return NEOResponse.parse_json(asteroids_res)


@pytest.fixture
def cache_file(tmp_path, monkeypatch):
    cache_path = tmp_path / "cache.json"
    monkeypatch.setattr("space.cache.CACHE_FILE", cache_path)
    return cache_path


def make_fake_apod_client(monkeypatch, response=None):
    fake_client = MagicMock()
    fake_client.__enter__.return_value = fake_client
    fake_client.get_apods.return_value = response
    monkeypatch.setattr("space.cli.ApiClient", lambda: fake_client)
    return fake_client


def make_fake_asteroids_client(monkeypatch, response=None):
    fake_client = MagicMock()
    fake_client.__enter__.return_value = fake_client
    fake_client.get_asteroids.return_value = response
    monkeypatch.setattr("space.cli.ApiClient", lambda: fake_client)
    return fake_client
