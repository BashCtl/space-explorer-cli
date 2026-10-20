from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from space.models import Apod, Asteroid


class Formatter:
    def __init__(self):
        self.console = Console()
        self.err_console = Console(stderr=True)

    def print_apods(self, apods: list[Apod]):
        for apod in apods:
            self.console.print()

            self.console.rule(
                f"[bold green]{apod.title}[/bold green]",
                align="left",
                style="bold cyan",
            )
            self.console.print(
                f"[bold][cyan]Date:[/cyan] [green]{apod.date}[/green][/bold]"
            )
            self.console.print(
                Panel(
                    Text(apod.explanation.removeprefix("Explanation:")),
                    title="[bold cyan]Explanation:[/bold cyan]",
                    border_style="blue",
                    expand=False,
                    style="#27D676",
                    padding=(1, 2),
                    width=90,
                )
            )
            self.console.print(
                "[cyan bold]Post link: [/cyan bold]",
                f"[link={apod.permalink} underline blue]{apod.permalink}[/link]\n",
            )

            if apod.media_type == "image":
                self.console.print(
                    "[cyan bold]Image link: [/cyan bold]",
                    f"[link={apod.hdurl} underline blue]{apod.title}[/link]",
                )

            elif apod.media_type == "video":
                self.console.print(
                    "[cyan bold]Video can be find by link: [/cyan bold]",
                    f"[link={apod.permalink} underline blue]{apod.permalink}[/link ]",
                )
        self.console.rule(style="bold cyan")

    def print_asteroids_table(self, asteroids: list[Asteroid]):
        table = Table(title="Asteroids", style="cyan")

        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Close Approach Date", style="green", justify="right")
        table.add_column("Relative Velocity km/h", style="green", justify="right")
        table.add_column("Miss Distance km", style="green", justify="right")
        table.add_column("Miss Distance Lunar", style="green", justify="right")
        table.add_column("Max Diameter km", style="green", justify="right")
        table.add_column("Potentially Hazardous", style="green", justify="center")

        for asteroid in asteroids:
            name = asteroid.name

            close_approach_date = asteroid.close_approach_data[0].close_approach_date
            kilometers_per_hour = f"{asteroid.close_approach_data[0].relative_velocity.kilometers_per_hour:,.2f}"
            miss_distance_km = (
                f"{asteroid.close_approach_data[0].miss_distance.kilometers:,.1f}"
            )
            miss_distance_lunar = (
                f"{asteroid.close_approach_data[0].miss_distance.lunar:,.0f}"
            )
            max_diameter_km = (
                f"{asteroid.estimated_diameter.kilometers.estimated_diameter_max:.2f}"
            )
            is_hazardous = (
                "[red]YES[/red]" if asteroid.is_potentially_hazardous_asteroid else "NO"
            )

            table.add_row(
                name,
                close_approach_date,
                kilometers_per_hour,
                miss_distance_km,
                miss_distance_lunar,
                max_diameter_km,
                is_hazardous,
            )
        self.console.print(table)

    def print_raw_json(self, json_data):
        self.console.print_json(data=json_data, indent=4)

    def print_error(self, exception: Exception):
        self.err_console.print(f"[red bold]Error: [/red bold] {exception!s}")
