from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from space.models import Apod


class Formatter:
    def __init__(self):
        self.console = Console()
        self.err_console = Console(stderr=True)

    def print_apods(self, apods: list[Apod]):
        for apod in apods:
            self.console.print()
         
            self.console.rule(f"[bold green]{apod.title}[/bold green]", align="left", style="bold cyan")
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


    def print_raw_json(self, json_data):
        self.console.print_json(data=json_data, indent=4)