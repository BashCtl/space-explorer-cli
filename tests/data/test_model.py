import pytest
from pydantic import ValidationError

from space.models import Apod


@pytest.fixture
def valid_data():
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


def test_parse_valid_data(valid_data):
    result = Apod.parse_json([valid_data])

    assert len(result) == 1
    assert isinstance(result[0], Apod)
    assert result[0].date == "2026-10-17"
    assert result[0].post_id == 123
    assert result[0].title == "A Beautiful Galaxy"
    assert result[0].media_type == "image"


def test_parse_multiple_records(valid_data):
    result = Apod.parse_json([valid_data, valid_data.copy()])

    assert len(result) == 2
    assert all(isinstance(item, Apod) for item in result)


def test_explanation_html_is_converted(valid_data):
    apod = Apod.parse_json([valid_data])[0]

    assert "<p>" not in apod.explanation
    assert "<b>" not in apod.explanation
    assert "beautiful" in apod.explanation
    assert "galaxy" in apod.explanation


def test_parse_empty_list():
    assert Apod.parse_json([]) == []


def test_missing_required_field(valid_data):
    invalid_data = valid_data.copy()
    del invalid_data["title"]

    with pytest.raises(ValidationError):
        Apod.parse_json([invalid_data])


def test_invalid_post_id(valid_data):
    invalid_data = valid_data.copy()
    invalid_data["post_id"] = "not-an-integer"

    with pytest.raises(ValidationError):
        Apod.parse_json([invalid_data])


def test_invalid_input_type(valid_data):
    with pytest.raises(ValidationError):
        Apod.parse_json(valid_data)


def test_invalid_record_in_list(valid_data):
    invalid_data = valid_data.copy()
    del invalid_data["url"]

    with pytest.raises(ValidationError):
        Apod.parse_json([valid_data, invalid_data])
