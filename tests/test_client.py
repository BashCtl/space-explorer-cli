from unittest.mock import Mock

import pytest

from space.client import ApiClient
from space.errors import ApiHttpError


def test_get_apod_return_json(monkeypatch, apod_res):

    expected_data = apod_res.copy()

    with ApiClient() as client:
        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_response.raise_for_status.return_value = None

        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr(client.session, "get", mock_get)

        result = client.get_apods("/feed-basic")

        assert result == expected_data

        mock_get.assert_called_once()
        mock_response.raise_for_status.assert_called_once_with()
        mock_response.json.assert_called_once_with()


def test_get_apod_raises_http_error(monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = ApiHttpError(
        "Invalid response status code."
    )

    with ApiClient() as client:
        monkeypatch.setattr(client.session, "get", Mock(return_value=mock_response))

        with pytest.raises(ApiHttpError, match="Invalid response status code."):
            client.get_apods("/feed-basic")
        mock_response.json.assert_not_called()


def test_context_manager_closes_session():
    with ApiClient() as client:
        session = client.session
        close = Mock(wraps=session.close)
        session.close = close

    close.assert_called_once_with()


def test_get_asteroids_return_json(monkeypatch, asteroids_res):

    expected_data = asteroids_res.copy()

    with ApiClient() as client:
        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_response.raise_for_status.return_value = None

        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr(client.session, "get", mock_get)

        result = client.get_asteroids("/feed")

        assert result == expected_data

        mock_get.assert_called_once()
        mock_response.raise_for_status.assert_called_once_with()
        mock_response.json.assert_called_once_with()


def test_get_asteroids_raises_http_error(monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = ApiHttpError(
        "Invalid response status code."
    )

    with ApiClient() as client:
        monkeypatch.setattr(client.session, "get", Mock(return_value=mock_response))

        with pytest.raises(ApiHttpError, match="Invalid response status code."):
            client.get_asteroids("/feed-basic")
        mock_response.json.assert_not_called()
