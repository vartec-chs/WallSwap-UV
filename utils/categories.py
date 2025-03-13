from bs4 import BeautifulSoup
from rich.table import Table
from config import console, logger
from models import Category
from utils.fetcher import fetch
from rich.progress import Progress, SpinnerColumn, TextColumn


def get_categories() -> list[Category]:
    console.rule("[bold cyan]Получаем категории...[/bold cyan]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Получаем категории...[/cyan]"),
        transient=True,
    ) as progress:
        task = progress.add_task("", total=None)  # Бесконечный лоадер
        response = fetch("https://wallpaperscraft.ru/")
        if not response:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        filter_div = soup.select_one(".filters")
        if not filter_div:
            logger.error(
                "Не удалось найти элемент с категориями. Структура сайта могла измениться."
            )
            return []
        categories = [
            Category(
                "".join(t for t in link.contents if isinstance(t, str)).strip(),
                f"https://wallpaperscraft.ru{link['href']}",
            )
            for link in filter_div.select(".filters__list .filter__link")
            if not link.get("href") == "javascript:;"
        ]

        # Дополнительные категории
        content_sidebar_shift = soup.select_one(".content-sidebar_shift")
        if content_sidebar_shift:
            for link in content_sidebar_shift.select(".filters__list .filter__link"):
                if not link.get("href") == "javascript:;":
                    categories.append(
                        Category(
                            "".join(
                                t for t in link.contents if isinstance(t, str)
                            ).strip(),
                            f"https://wallpaperscraft.ru{link['href']}",
                        )
                    )

        categories.append(Category("Все категории", "https://wallpaperscraft.ru"))

        progress.remove_task(task)

    if categories:
        console.print(
            f"[bold white]Найдено категорий:[/bold white] [underline cyan]{len(categories)}[/underline cyan]",
            end="",
        )
    else:
        logger.error("Не удалось найти категории. Структура сайта могла измениться.")
    return categories


def show_categories(categories: list[Category]):
    console.rule("[bold blue]Выбор категории[/bold blue]")
    table = Table()
    table.add_column("Номер", justify="center", style="bold yellow")
    table.add_column("Название", justify="center", style="bold cyan")
    table.add_column("URL", justify="center", style="bold dim")
    for i, cat in enumerate(categories, start=1):
        table.add_row(
            str(i),
            cat.name,
            cat.url,
            end_section=(i == 27) or (i == len(categories) - 1),
        )
    console.print(table)
