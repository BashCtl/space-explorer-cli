import json
from pathlib import Path

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
