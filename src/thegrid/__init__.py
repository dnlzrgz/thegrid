from datetime import datetime
from typing_extensions import Annotated

import typer

GRID_WIDTH = 52  # weeks per year


def calculate_weeks_lived(birthday: str) -> int:
    birthday_date = datetime.strptime(birthday, "%Y-%m-%d")
    today = datetime.now()
    delta = today - birthday_date

    return delta.days // 7


def main(
    birthday: Annotated[
        str,
        typer.Option(
            "--birthday",
            help="birthday date (%Y-%m-%d)",
        ),
    ],
    life_expectancy: Annotated[
        int,
        typer.Option(
            "--expectancy",
            min=1,
            max=100,
            help="life expectancy in years.",
        ),
    ] = 90,
) -> None:
    """
    Prints a grid that represents the total number of weeks
    lived based on the birthday.
    """

    weeks_lived = calculate_weeks_lived(birthday)
    if weeks_lived > life_expectancy * GRID_WIDTH:
        print("you have lived longer than your expected lifespan.")
        return

    print(f"you have lived: {weeks_lived} weeks")
    grid = [
        ["x" if (i * GRID_WIDTH + j) < weeks_lived else "·" for j in range(GRID_WIDTH)]
        for i in range(life_expectancy)
    ]

    for row in grid:
        print("".join(row))


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
