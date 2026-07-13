"""Visual layer: banner, color theme, and console components for SaXwiT."""

import pyfiglet
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich import box

THEME = Theme(
    {
        "brand": "bold bright_cyan",
        "accent": "bold magenta",
        "ok": "bold bright_green",
        "warn": "bold yellow",
        "bad": "bold red",
        "dim": "grey58",
        "info": "bright_blue",
        "title": "bold white on grey11",
    }
)

console = Console(theme=THEME)


def render_banner() -> None:
    """Print the 'SaXwiT' ASCII banner with a cyan -> magenta color gradient."""
    fig = pyfiglet.Figlet(font="slant")
    ascii_art = fig.renderText("SaXwiT")

    lines = [l for l in ascii_art.split("\n") if l.strip("\n")]
    colors = ["bright_cyan", "cyan", "medium_purple1", "magenta", "bright_magenta"]

    art_text = Text()
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        art_text.append(line + "\n", style=f"bold {color}")

    author = Text(
        "Author: AldX",
        style="dim italic",
    )

    console.print(Align.center(art_text))
    console.print(Align.center(author))
    console.print()


def section(title: str, subtitle: str = "") -> None:
    body = f"[title] {title} [/title]"
    if subtitle:
        body += f"\n[dim]{subtitle}[/dim]"
    console.print(Panel(body, box=box.HEAVY, border_style="brand", expand=True))
