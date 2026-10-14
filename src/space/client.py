import os

import requests
from dotenv import load_dotenv

from space.errors import (
    ApiConnectionError,
    ApiHttpError,
    ApiTimeoutError,
    ApiValueError,
)

load_dotenv()


class ApiClient:
    URL = "https://science.nasa.gov"

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update({"X-Api-Key": os.getenv("API_KEY", "")})

    def get(self, endpoint: str, timeout: int = 10, **params):
        try:
            url = self.URL + endpoint
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.Timeout as exc:
            raise ApiTimeoutError("Timeout occures, the server was too slow.") from exc
        except requests.ConnectionError as exc:
            raise ApiConnectionError("No network or DNS problem.") from exc
        except requests.HTTPError as exc:
            raise ApiHttpError("Invalid response status code.") from exc
        except ValueError as exc:
            raise ApiValueError("Response body is not a valid JSON.") from exc

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
