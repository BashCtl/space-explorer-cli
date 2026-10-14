import typer


app = typer.Typer()


@app.command()
def apod(
    date: str = typer.Option(
        None, "--date", help="Show APOD for one day. Format: YYYY-MM-DD"
    ),
    recent: int = typer.Option(
        1, "--recent", help="Show the latest N entries(1 to 25). --recent <N>"
    ),
    from_date: str = typer.Option(
        None, "--from", help="Show entries from date. Format YYYY-MM-DD"
    ),
    to_date: str = typer.Option(
        None, "--to", help="Show entries to date. Format YYYY-MM-DD"
    ),
    timeout: int = typer.Option(
        10, "--timeout", help="Seconds before the request is abandoned. Default: 10"
    ),
    raw: bool = typer.Option(False, "--raw", help="Print the raw response JSON"),
):
    pass


@app.command()
def asteroids():
    pass


if __name__ == "__main__":
    app()
