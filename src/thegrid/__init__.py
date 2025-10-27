from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from typing_extensions import Annotated

GRID_WIDTH = 52  # Weeks in a year

# Initialize the consoles for standard and error output
console = Console(record=True)
err_console = Console(stderr=True)


def calculate_weeks_lived(birthday: str) -> int:
    """
    Calculates the total weeks lived based on the received birthday date without
    accounting for leap years.
    """
    birthday_date = datetime.strptime(birthday, "%Y-%m-%d")
    today = datetime.now()
    delta = today - birthday_date

    return delta.days // 7


def generate_grid(weeks_lived: int, life_expectancy: int) -> list[list[str]]:
    """
    Generates a grid representing weeks lived vs the expected lifespan.
    """
    return [
        ["x" if (i * GRID_WIDTH + j) < weeks_lived else "·" for j in range(GRID_WIDTH)]
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
) -> None:
    """
    Generates a grid representing the total number of weeks lived based on your birthday
    and expected lifespan.
    """

    try:
        weeks_lived = calculate_weeks_lived(birthday)
    except Exception as e:
        err_console.print(f"something went wrong while parsing your birthday date: {e}")
        raise typer.Exit()

    if weeks_lived > life_expectancy * GRID_WIDTH:
        err_console.print(
            f"you have exceeded your expected lifespan of {life_expectancy} years."
        )
        raise typer.Exit()

    grid = generate_grid(weeks_lived, life_expectancy)
    grid_panel = Panel.fit(
        "\n".join("".join(row) for row in grid),
        title="the grid",
        title_align="left",
        safe_box=True,
        padding=(1, 2),
    )

    if print_summary:
        weeks_to_live = (life_expectancy * GRID_WIDTH) - weeks_lived
        summary_panel = Panel.fit(
            f"lived: {weeks_lived} weeks.\nto live: {weeks_to_live} weeks.\n",
            title="summary",
            title_align="left",
            safe_box=True,
            padding=(1, 2),
        )

        columns = Columns([grid_panel, summary_panel])
        console.print(columns)
        return

    console.print(grid_panel)


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
