from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from space.errors import ApiValueError, SpaceTypeError


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


def compute_neo_range(days: int):
    try:
        if days > 7:
            raise ApiValueError("Days ahead parameter can not be bigger than 7.")
        if days < 0:
            raise ApiValueError("Days ahead parameter must be a postive integer")
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        return start_date, end_date

    except TypeError as exc:
        raise SpaceTypeError("Days param must be and integer number.") from exc


def parse_neo_date(date: str):
    try:
        return datetime.strptime(date, "%Y-%m-%d")
    except ValueError as exc:
        raise ApiValueError("Invalid date format. Must be 'YYYY-MM-DD'.") from exc
