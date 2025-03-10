import os
import random
import re
import sys
import requests
import ctypes
import logging
from bs4 import BeautifulSoup
from dataclasses import dataclass
from rich.console import Console
from rich.prompt import Prompt
from rich.logging import RichHandler
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    DownloadColumn,
)

# =====================[ НАСТРОЙКА ]=====================
console = Console()
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[RichHandler(console=console)],
)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.0.0 Safari/537.36"
}


# =====================[ ДАТАКЛАСС ]=====================
@dataclass
class Category:
    name: str
    url: str


# =====================[ ФУНКЦИИ ]=====================


def fetch(url: str) -> requests.Response | None:
    """Обертка над requests.get с обработкой ошибок."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к {url}: {e}")
        return None


def get_categories() -> list[Category]:
    """Получаем список категорий обоев."""
    console.rule("[bold cyan]Получаем категории...[/bold cyan]")
    response = fetch("https://wallpaperscraft.ru/")
    if not response:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    categories = [
        Category(
            "".join(t for t in link.contents if isinstance(t, str)).strip(),
            f"https://wallpaperscraft.ru{link['href']}",
        )
        for link in soup.select(".filters__list .filter__link")
    ]

    if categories:
        console.print(f"[bold cyan]Найдено категорий:[/bold cyan] {len(categories)}")
    else:
        logger.error("Не удалось найти категории. Структура сайта могла измениться.")
    return categories


def get_random_wallpaper(category_url: str) -> str | None:
    """Ищем случайную обложку из выбранной категории."""
    console.rule("[bold violet]Поиск обоев...[/bold violet]")

    response = fetch(category_url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Определяем последнюю страницу
    pager_items = soup.select(".pager__item")
    last_page = 1
    if len(pager_items) >= 4:
        href = pager_items[3].select_one("a")["href"]
        last_page = int(href.split("page")[-1])

    console.print(f"[bold gray]Всего страниц:[/bold gray] [yellow]{last_page}[/yellow]")
    page = random.randint(1, last_page)
    console.print(
        f"[bold violet]Выбрана страница:[/bold violet] [yellow]{page}[/yellow]"
    )

    response = fetch(f"{category_url}/page{page}")
    if not response:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    wallpapers = [a["href"] for a in soup.select(".wallpapers__link")]
    if not wallpapers:
        console.print("[bold red]Нет обоев на этой странице.[/bold red]")
        return None

    random_page = random.choice(wallpapers)
    console.print(
        f"[bold violet]Выбрана ссылка на обои:[/bold violet] [yellow]{random_page}[/yellow]"
    )

    return get_image_url(f"https://wallpaperscraft.ru{random_page}")


def get_image_url(wallpaper_page_url: str) -> str | None:
    """Получаем прямую ссылку на изображение с страницы обоев."""
    response = fetch(wallpaper_page_url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    img_link = None

    # Вариант 1
    info = soup.select_one(".wallpaper-info .wallpaper-table__row")
    if info:
        img_link = info.select(".wallpaper-table__cell")[1].select_one("a")["href"]

    # Вариант 2
    if not img_link:
        toolbar = soup.select_one(".gui-toolbar .gui-button")
        if toolbar:
            img_link = toolbar["href"]
            if img_link.endswith(".jpg"):
                console.print(
                    f"[bold pink]Прямая ссылка на изображение:[/bold pink] [green]{img_link}[/green]"
                )
                return img_link

    if not img_link:
        console.print("[bold red]Не удалось найти ссылку на изображение.[/bold red]")
        return None

    if not img_link.startswith("https://"):
        url = f"https://wallpaperscraft.ru{img_link}"
    else:
        url = img_link

    console.print(f"[bold pink]Выбрано изображение: {url}[/bold pink]")
    response_w = fetch(url)
    if not response_w:
        return None
    soup_w = BeautifulSoup(response_w.text, "html.parser")
    wallpaper_w_tag = soup_w.select_one(".wallpaper")
    wrapper_button = wallpaper_w_tag.select_one(".gui-toolbar div")
    img_link = wrapper_button.select_one("a").get("href")
    if not img_link:
        console.print(
            "[bold red]Не удалось найти прямую ссылку на изображение.[/bold red]"
        )
        return None

    console.print(
        f"[bold pink]Прямая ссылка на изображение:[/bold pink] [green]{img_link}[/green]"
    )
    return img_link


def download_wallpaper(image_url: str, save_path: str) -> bool:
    """Скачиваем обои с отображением прогресса, скорости и объёма."""
    console.rule("[bold green]Скачивание обоев...[/bold green]")

    try:
        with requests.get(
            image_url, headers=HEADERS, stream=True, timeout=10
        ) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            if total_size == 0:
                console.print(
                    "[bold red]Ошибка: пустой файл или неизвестный размер.[/bold red]"
                )
                return False

            with (
                open(save_path, "wb") as file,
                Progress(
                    SpinnerColumn(style="cyan"),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(bar_width=40, style="magenta"),
                    DownloadColumn(),  # показывает объем данных, например "5.3 MB / 20.0 MB"
                    TransferSpeedColumn(),  # показывает скорость загрузки
                    TimeRemainingColumn(),  # оценка оставшегося времени
                    transient=True,
                ) as progress,
            ):
                task = progress.add_task("Загрузка", total=total_size)

                for chunk in response.iter_content(chunk_size=8192):  # 8KB буфер
                    if chunk:
                        file.write(chunk)
                        progress.update(task, advance=len(chunk))

        console.print("[bold green]✅ Скачивание завершено![/bold green]")
        return True

    except requests.RequestException as e:
        logger.error(f"Ошибка загрузки: {e}")
        console.print("[bold red]❌ Ошибка при скачивании файла![/bold red]")
        return False


def set_wallpaper(image_path: str):
    """Установка обоев на рабочий стол."""
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    console.print("[bold green]Обои успешно установлены![/bold green]")


# =====================[ ОСНОВНОЙ ПРОЦЕСС ]=====================
def main():
    sys_choice = sys.argv[1] if len(sys.argv) > 1 else None
    categories = get_categories()
    if not categories:
        logger.error("Категории не найдены!")
        return

    if not sys_choice:
        console.rule("[bold blue]Выбор категории[/bold blue]")
        for i, cat in enumerate(categories, start=1):
            console.print(
                f"[bold yellow]{i}.[/bold yellow] [cyan]{cat.name}[/cyan] [dim]{cat.url}[/dim]"
            )
    elif sys_choice == "-c":
        console.rule("[bold blue]Выбор категории[/bold blue]")
        for i, cat in enumerate(categories, start=1):
            console.print(
                f"[bold yellow]{i}.[/bold yellow] [cyan]{cat.name}[/cyan] [dim]{cat.url}[/dim]"
            )
        return

    while True:
        try:
            choice = 0

            if sys_choice:
                choice = int(sys_choice) - 1
                if 0 <= choice < len(categories):
                    break
                else:
                    return console.print(
                        f"[bold red]Ошибка: Введите число в пределах списка.[/bold red]"
                    )
            else:
                choice = (
                    int(Prompt.ask("[bold green]Введите номер категории[/bold green]"))
                    - 1
                )

            if 0 <= choice < len(categories):
                break
            else:
                console.print(
                    "[bold red]Ошибка: Введите число в пределах списка.[/bold red]"
                )

        except ValueError:
            console.print("[bold red]Неверный ввод. Введите число![/bold red]")

    category = categories[choice]
    console.print(
        f"[bold magenta]Загружаем обои из категории:[/bold magenta] [cyan]{category.name}[/cyan]"
    )

    wallpaper_url = get_random_wallpaper(category.url)
    if not wallpaper_url:
        console.print("[bold red]Не удалось получить ссылку на обои.[/bold red]")
        return

    save_path = os.path.join(os.path.expanduser("~"), "wallpaper.jpg")
    if download_wallpaper(wallpaper_url, save_path):
        set_wallpaper(save_path)
    else:
        console.print("[bold red]Ошибка при скачивании обоев.[/bold red]")


if __name__ == "__main__":
    main()
