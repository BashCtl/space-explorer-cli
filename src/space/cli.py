import typer

from space.client import ApiClient, Endpoints
from space.errors import ApiError, ApiValueError
from space.formatter import Formatter
from space.models import Apod, NEOResponse
from space.parser import compute_neo_range, parse_date, parse_neo_date, parse_neo_feed

app = typer.Typer()


@app.command()
def apod(
    date: str = typer.Option(
        None, "--date", help="Show APOD for one day. Format: YYYY-MM-DD"
    ),
    recent: int = typer.Option(
        ApiClient.PER_PAGE,
        "--recent",
        help="Show the latest N entries(1 to 25). --recent <N>",
    ),
    date_from: str = typer.Option(
        None, "--from", help="Show entries from date. Format YYYY-MM-DD"
    ),
    date_to: str = typer.Option(
        None, "--to", help="Show entries to date. Format YYYY-MM-DD"
    ),
    timeout: int = typer.Option(
        10, "--timeout", help="Seconds before the request is abandoned. Default: 10"
    ),
    raw: bool = typer.Option(False, "--raw", help="Print the raw response JSON"),
):
    formatter = Formatter()
    try:
        params = {}
        if date is not None:
            date = parse_date(date)
        if recent is not None:
            params["per_page"] = recent
        if date_from is not None:
            params["date_from"] = parse_date(date_from)
        if date_to is not None:
            params["date_to"] = parse_date(date_to)

        with ApiClient() as client:
            response = client.get_apods(
                Endpoints.APOD_BASIC, date=date, timeout=timeout, **params
            )

            if raw:
                formatter.print_raw_json(response)
            else:
                apods = Apod.parse_json(response)
                formatter.print_apods(apods)

    except ApiError as exc:
        formatter.print_error(exc)


@app.command()
def asteroids(
    days: int = typer.Option(
        None, "--days", help="Number of days to look ahead. Limit is 7 days ahead"
    ),
    start: str = typer.Option(
        None, "--start", help="Start of the date range. Format YYYY-MM-DD"
    ),
    end: str = typer.Option(
        None,
        "--end",
        help="End of the date range.Limit 7 days after start date. Format YYYY-MM-DD",
    ),
    hazardous: bool = typer.Option(
        False, "--hazardous-only", help="Show only potentially hazardous asteroids"
    ),
    limit: int = typer.Option(10, "--limit", help="Show only the N closest"),
    timeout: int = typer.Option(
        10, "--timeout", help="Seconds before the request is abandoned. Default: 10"
    ),
):
    formatter = Formatter()
    try:
        params = {}
        if days is not None and end is not None:
            raise ApiValueError("'--days' and '--end' can not be used together.")
        if days is not None:
            start_date, end_date = compute_neo_range(days)
            params["start_date"] = start_date
            params["end_date"] = end_date

        if start is not None and end is not None:
            params["start_date"] = parse_neo_date(start)
            params["end_date"] = parse_neo_date(end)

        with ApiClient() as client:
            response = client.get_asteroids(
                Endpoints.NEO_FEED, timeout=timeout, **params
            )
            neo_feed_res = NEOResponse.parse_json(response)
            asteroids_list = parse_neo_feed(
                neo_feed_res, hazardous=hazardous, limit=limit
            )
            print(asteroids_list)
    except ApiError as exc:
        formatter.print_error(exc)


if __name__ == "__main__":
    app()
