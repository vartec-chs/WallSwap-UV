import random
from threading import Thread
import requests
import ctypes
from bs4 import BeautifulSoup
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    DownloadColumn,
)

from config import console, logger, HEADERS
from utils.clear_cmd import clear_cmd
from utils.fetcher import fetch


def get_random_wallpaper(category_url: str, category_name: str) -> str | None:
    """Ищем случайную обложку из выбранной категории."""
    console.rule("[bold violet]Поиск обоев...[/bold violet]")

    console.print(
        f"[bold gray]Выбрана категория:[/bold gray] [yellow]{category_name}[/yellow]"
    )

    random_page = None

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Поиск страниц и получения рандомных обоев...[/cyan]"),
        transient=True,
    ) as progress:
        task = progress.add_task("", total=None)  # Бесконечный лоадер
        response = fetch(category_url)
        if not response:
            progress.remove_task(task)
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        # Определяем последнюю страницу
        pager_items = soup.select(".pager__item")
        last_page = 1
        if len(pager_items) >= 4:
            href = pager_items[3].select_one("a")["href"]
            last_page = int(href.split("page")[-1])

        # console.print(f"[bold gray]Всего страниц:[/bold gray] [yellow]{last_page}[/yellow]")
        page = random.randint(1, last_page)
        # console.print(
        #     f"[bold violet]Выбрана страница:[/bold violet] [yellow]{page}[/yellow]"
        # )

        if category_url == "https://wallpaperscraft.ru":
            url = f"https://wallpaperscraft.ru/all/page{page}"
        else:
            url = f"{category_url}/page{page}"
        # console.print(
        #     f"[bold violet]Выбрана страница:[/bold violet] [yellow]{url}[/yellow]"
        # )

        response = fetch(url)
        if not response:
            progress.remove_task(task)
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        wallpapers = [a["href"] for a in soup.select(".wallpapers__link")]
        if not wallpapers:
            progress.remove_task(task)
            console.print("[bold red]Нет обоев на этой странице.[/bold red]")
            return None

        random_page = random.choice(wallpapers)
        # console.print(
        #     f"[bold violet]Выбрана ссылка на обои:[/bold violet] [yellow]{random_page}[/yellow]"
        # )
        progress.remove_task(task)

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
            console.print("\n")
            try:
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
            except Exception as e:
                logger.error(f"Ошибка при скачивании файла: {e}")
                return False

        clear_cmd()
        console.print("[bold green]✅ Скачивание завершено![/bold green]", end="")
        return True

    except requests.RequestException as e:
        logger.error(f"Ошибка загрузки: {e}")
        return False


def set_wallpaper(image_path: str):
    """Установка обоев на рабочий стол."""
    # ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    thread = Thread(
        target=ctypes.windll.user32.SystemParametersInfoW, args=(20, 0, image_path, 3)
    )
    thread.start()
