import typer

from space.client import ApiClient, Endpoints
from space.errors import ApiError
from space.formatter import Formatter
from space.models import Apod
from space.parser import parse_date

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
            response = client.get(
                Endpoints.APOD_BASIC, date=date, timeout=timeout, **params
            )

            if raw:
                formatter.print_raw_json(response)
            else:
                apods = Apod.parse_json(response)
                formatter.print_apods(apods)

    except ApiError as exc:
        print(exc)


@app.command()
def asteroids():
    pass


if __name__ == "__main__":
    app()
