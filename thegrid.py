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

GRID_WIDTH = 52  # Weeks in a year

# Initialize the consoles for standard and error output
console = Console(record=True, emoji=True)
err_console = Console(stderr=True)


def calculate_weeks_lived(birthday_date: datetime) -> int:
    today = datetime.now()
    delta = today - birthday_date
    return delta.days // 7


def calculate_year_of_death(birthday_date: datetime, life_expectancy: int) -> int:
    return birthday_date.year + life_expectancy


def generate_grid(
    weeks_lived: int,
    life_expectancy: int,
    symbols: dict[str, str],
) -> list[list[str]]:
    """
    Generates a grid representing weeks lived vs the expected lifespan.
    """
    return [
        [
            symbols["lived"] if (i * GRID_WIDTH + j) < weeks_lived else symbols["left"]
            for j in range(GRID_WIDTH)
        ]
        for i in range(life_expectancy)
    ]


def main(
    birthday: Annotated[
        str,
        typer.Option(
            "--birthday",
            help="birthday date (YYYY-MM-DD)",
        ),
    ],
    life_expectancy: Annotated[
        int,
        typer.Option(
            "--life-expectancy",
            min=1,
            max=100,
            show_default=True,
            help="expected lifespan in years.",
        ),
    ] = 90,
    print_summary: Annotated[
        bool,
        typer.Option(
            "--summary",
            show_default=True,
            help="display a summary of weeks lived and so on.",
        ),
    ] = False,
    lived_symbol: Annotated[
        str,
        typer.Option(
            "--lived",
            show_default=True,
            help="symbol used to represent weeks lived.",
        ),
    ] = "×",
    left_symbol: Annotated[
        str,
        typer.Option(
            "--left",
            show_default=True,
            help="symbol used to represent weeks left to live.",
        ),
    ] = "·",
    export_svg: Annotated[
        Path | None,
        typer.Option(
            "--export-svg",
            show_default=True,
            help="write svg to the path specified.",
        ),
    ] = None,
) -> None:
    """
    Generates a grid representing the total number of weeks lived based on your birthday
    and expected lifespan.
    """

    try:
        birthday_date = datetime.strptime(birthday, "%Y-%m-%d")
    except Exception as e:
        err_console.print(f"something went wrong while parsing your birthday date: {e}")
        raise typer.Exit()

    total_weeks = life_expectancy * GRID_WIDTH
    weeks_lived = calculate_weeks_lived(birthday_date)
    year_of_death = calculate_year_of_death(birthday_date, life_expectancy)
    if weeks_lived > total_weeks:
        err_console.print(
            f"you have exceeded your expected lifespan of {life_expectancy} years."
        )
        raise typer.Exit()

    grid = generate_grid(
        weeks_lived, life_expectancy, {"lived": lived_symbol, "left": left_symbol}
    )
    grid_panel = Panel.fit(
        "\n".join("".join(row) for row in grid),
        title="the grid",
        title_align="left",
        subtitle=f"{birthday_date.year}-{year_of_death}",
        subtitle_align="right",
        safe_box=True,
        padding=(1, 2),
    )

    if print_summary:
        weeks_to_live = total_weeks - weeks_lived
        summary_panel = Panel.fit(
            f"{weeks_lived} weeks lived.\n{weeks_to_live} weeks left.",
            title="summary",
            title_align="left",
            safe_box=True,
            padding=(1, 2),
        )

        columns = Columns([summary_panel, grid_panel])
        console.print(columns)
    else:
        console.print(grid_panel)

    if export_svg:
        console.save_svg(path=f"{export_svg}", theme=DEFAULT_TERMINAL_THEME)


if __name__ == "__main__":
    typer.run(main)
