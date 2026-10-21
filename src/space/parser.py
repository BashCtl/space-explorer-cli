from datetime import datetime, timedelta

from space.errors import ApiValueError, SpaceTypeError
from space.models import Asteroid, NEOResponse


def parse_apod_date(input_date: str) -> str:
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


def parse_neo_date(date: str) :
    try:
        return datetime.strptime(date, "%Y-%m-%d").date().isoformat()
    except ValueError as exc:
        raise ApiValueError("Invalid date format. Must be 'YYYY-MM-DD'.") from exc


def parse_neo_feed(
    neo_response: "NEOResponse", hazardous=False, limit=10
) -> list[Asteroid]:
    result: list[Asteroid] = []
    for asteroids_list in neo_response.near_earth_objects.values():
        result.extend(asteroids_list)

    result.sort(key=lambda a: a.close_approach_data[0].miss_distance.kilometers)
    if hazardous:
        result = [asteroid for asteroid in result if asteroid.is_potentially_hazardous_asteroid]

    return result[:limit]
