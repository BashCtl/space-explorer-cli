import pytest
from pydantic import ValidationError

from space.models import Apod, NEOResponse


@pytest.fixture
def apod_valid_data():
    return {
        "date": "2026-10-17",
        "post_id": 123,
        "title": "A Beautiful Galaxy",
        "permalink": "https://example.com/apod/123",
        "media_type": "image",
        "explanation": "<p>A beautiful <b>galaxy</b>.</p>",
        "credit": "NASA",
        "copyright": "NASA",
        "alt": "A spiral galaxy in deep space",
        "url": "https://example.com/image.jpg",
        "hdurl": "https://example.com/image-hd.jpg",
        "basic_html": "<img src='image.jpg'>",
        "basic_html_url": "https://example.com/basic.html",
    }


def test_parse_apod_valid_data(apod_valid_data):
    result = Apod.parse_json([apod_valid_data])

    assert len(result) == 1
    assert isinstance(result[0], Apod)
    assert result[0].date == "2026-10-17"
    assert result[0].post_id == 123
    assert result[0].title == "A Beautiful Galaxy"
    assert result[0].media_type == "image"


def test_parse_apod_multiple_records(apod_valid_data):
    result = Apod.parse_json([apod_valid_data, apod_valid_data.copy()])

    assert len(result) == 2
    assert all(isinstance(item, Apod) for item in result)


def test_apod_explanation_html_is_converted(apod_valid_data):
    apod = Apod.parse_json([apod_valid_data])[0]

    assert "<p>" not in apod.explanation
    assert "<b>" not in apod.explanation
    assert "beautiful" in apod.explanation
    assert "galaxy" in apod.explanation


def test_apod_parse_empty_list():
    assert Apod.parse_json([]) == []


def test_apod_missing_required_field(apod_valid_data):
    invalid_data = apod_valid_data.copy()
    del invalid_data["title"]

    with pytest.raises(ValidationError):
        Apod.parse_json([invalid_data])


def test_apod_invalid_post_id(apod_valid_data):
    invalid_data = apod_valid_data.copy()
    invalid_data["post_id"] = "not-an-integer"

    with pytest.raises(ValidationError):
        Apod.parse_json([invalid_data])


def test_apod_invalid_input_type(apod_valid_data):
    with pytest.raises(ValidationError):
        Apod.parse_json(apod_valid_data)


def test_apod_invalid_record_in_list(apod_valid_data):
    invalid_data = apod_valid_data.copy()
    del invalid_data["url"]

    with pytest.raises(ValidationError):
        Apod.parse_json([apod_valid_data, invalid_data])


def test_parse_asteroids_valid_data(asteroids_res):
    result = NEOResponse.parse_json(asteroids_res)

    assert isinstance(result, NEOResponse)
    assert len(result.near_earth_objects) == 2
    assert result.element_count == 11
    assert next(iter(result.near_earth_objects.values()))[0].name == "(2009 UY17)"


def test_asteroids_parse_empty_dict():
    with pytest.raises(ValidationError):
        NEOResponse.parse_json({})


def test_asteroids_missing_required_field(asteroids_res):
    invalid_data = asteroids_res.copy()
    del invalid_data["element_count"]

    with pytest.raises(ValidationError):
        NEOResponse.parse_json([invalid_data])
