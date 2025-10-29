#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "typer",
# ]
# ///

from datetime import datetime
from pathlib import Path

import typer
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.terminal_theme import DEFAULT_TERMINAL_THEME
from typing_extensions import Annotated

GRID_WIDTH = 52  # Number of weeks in a year (grid's width).


# Output consoles.
console = Console(record=True, emoji=True)
err_console = Console(stderr=True)


def calculate_weeks_lived(birthday_date: datetime) -> int:
    delta = datetime.now() - birthday_date
    return delta.days // 7


def calculate_year_of_death(birthday_date: datetime, life_expectancy: int) -> int:
    return birthday_date.year + life_expectancy


def generate_grid(
    weeks_lived: int,
    life_expectancy: int,
    symbols: dict[str, str],
) -> list[list[str]]:
    """
    Create grid for weeks lived vs life expectancy.
    """
    return [
        [
            symbols["lived"] if (i * GRID_WIDTH + j) < weeks_lived else symbols["left"]
            for j in range(GRID_WIDTH)
        ]
        for i in range(life_expectancy)
    ]


def create_custom_panel(content: str, title: str, subtitle: str = "") -> Panel:
    return Panel.fit(
        content,
        title=title,
        title_align="left",
        subtitle=subtitle,
        subtitle_align="right",
        safe_box=True,
        padding=(1, 2),
    )


def main(
    birthday: Annotated[
        str,
        typer.Option(
            "--birthday",
            help="Birthday (format: YYYY-MM-DD).",
        ),
    ],
    life_expectancy: Annotated[
        int,
        typer.Option(
            "--life-expectancy",
            min=1,
            max=100,
            show_default=True,
            help="Expected lifespan in whole years.",
        ),
    ] = 90,
    grid_title: Annotated[
        str,
        typer.Option(
            "--grid-title",
            show_default=True,
            help="Title for grid's panel.",
        ),
    ] = "the grid",
    lived_symbol: Annotated[
        str,
        typer.Option(
            "--lived",
            show_default=True,
            help="Symbol for weeks lived.",
        ),
    ] = "×",
    left_symbol: Annotated[
        str,
        typer.Option(
            "--left",
            show_default=True,
            help="Symbol for weeks left to live.",
        ),
    ] = "·",
    summary_title: Annotated[
        str,
        typer.Option(
            "--summary-title",
            show_default=True,
            help="Title for summary's panel.",
        ),
    ] = "summary",
    print_summary: Annotated[
        bool,
        typer.Option(
            "--summary",
            show_default=True,
            help="Display summary of weeks lived.",
        ),
    ] = False,
    export_svg: Annotated[
        Path | None,
        typer.Option(
            "--export-svg",
            show_default=True,
            help="Path to save SVG.",
        ),
    ] = None,
) -> None:
    """
    Generate a grid of weeks lived based on birthday and life expectancy.
    """

    try:
        birthday_date = datetime.strptime(birthday, "%Y-%m-%d")
    except Exception as e:
        err_console.print(f"Invalid birthday format received: {e}")
        raise typer.Exit()

    total_weeks = life_expectancy * GRID_WIDTH
    weeks_lived = calculate_weeks_lived(birthday_date)
    year_of_death = calculate_year_of_death(birthday_date, life_expectancy)
    if weeks_lived > total_weeks:
        err_console.print(f"Exceeded expected lifespan of {life_expectancy} years.")
        raise typer.Exit()

    grid = generate_grid(
        weeks_lived,
        life_expectancy,
        {
            "lived": lived_symbol,
            "left": left_symbol,
        },
    )
    grid_panel = create_custom_panel(
        content="\n".join("".join(row) for row in grid),
        title=grid_title,
        subtitle=f"{birthday_date.year}-{year_of_death}",
    )

    output = []
    if print_summary:
        weeks_to_live = total_weeks - weeks_lived
        summary_panel = create_custom_panel(
            content=f"{weeks_lived} weeks lived.\n{weeks_to_live} weeks left.",
            title=summary_title,
            subtitle="",
        )
        output.append(summary_panel)

    output.append(grid_panel)
    console.print(Columns(output))

    if export_svg:
        console.save_svg(path=f"{export_svg}", theme=DEFAULT_TERMINAL_THEME)


if __name__ == "__main__":
    typer.run(main)
