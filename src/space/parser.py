from datetime import datetime

from bs4 import BeautifulSoup

from space.errors import ApiValueError


def html_to_string(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(" ", strip=True)


def parse_date(input_date: str) -> str:
    try:
        date_object = datetime.strptime(input_date, "%Y-%m-%d")
        return date_object.strftime("%y%m%d")
    except ValueError as exc:
        raise ApiValueError(
            f"Invalid date {input_date!r}. Expected format: YYYY-MM-DD"
        ) from exc
