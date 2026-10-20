import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

TEST_DATA = Path(__file__).parent / "data"


@pytest.fixture()
def apod_res():
    with open(TEST_DATA / "apod_list.json") as file:
        return json.load(file)


@pytest.fixture()
def asteroids_res():
    with open(TEST_DATA / "neo_feed.json") as file:
        return json.load(file)


def make_fake_apod_client(monkeypatch, response=None):
    fake_client = MagicMock()
    fake_client.__enter__.return_value = fake_client
    fake_client.get_apods.return_value = response
    monkeypatch.setattr("space.cli.ApiClient", lambda: fake_client)
    return fake_client
