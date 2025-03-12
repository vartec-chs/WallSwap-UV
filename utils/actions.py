import time
import keyboard
from rich.panel import Panel
from config import console
from models import WallpaperHistory
from enum import Enum


class ActionKey(Enum):
    NEXT = "next"
    PREVIOUS = "previous"
    EXIT = "exit"
    CATEGORY = "category"
    INFO = "info"
    DELETE_HISTORY = "delete_history"
    HELP = "help"
    CONFIG_EDIT = "config_edit"


def show_help():
    help_text = """
    [bold cyan]Доступные команды:[/bold cyan]

    [bold yellow]Shift[/bold yellow] - Загрузить следующие обои
    [bold yellow]Backspace[/bold yellow] - Вернуться к предыдущим обоям
    [bold yellow]Esc[/bold yellow] - Выйти из программы
    [bold yellow]h[/bold yellow] - Показать эту справку
    [bold yellow]c[/bold yellow] - Изменить категорию обоев
    [bold yellow]i[/bold yellow] - Показать информацию о текущих обоях,
    [bold yellow]d[/bold yellow] - Удалить историю обоев
    [bold yellow]s[/bold yellow] - Отредактировать конфигурацию
    """
    console.print(Panel(help_text, title="Справка", border_style="green"))


def wait_for_key_press() -> ActionKey:
    show_help()
    console.print("\n[bold yellow]Нажмите клавишу из списка:", end=" ")
    while True:
        event = keyboard.read_event()
        if event.event_type == "down":
            if event.name in ["shift", "right shift", "left shift"]:
                console.print(
                    "[bold yellow]нажата клавиша [bold white]Shift[/bold white][/bold yellow]"
                )
                return ActionKey.NEXT
            elif event.name == "backspace":
                console.print(
                    "[bold yellow]нажата клавиша [bold white]Backspace[/bold white][/bold yellow]"
                )
                return ActionKey.PREVIOUS
            elif event.name == "esc":
                console.print(
                    "[bold yellow]нажата клавиша [bold white]Esc[/bold white][/bold yellow]"
                )
                return ActionKey.EXIT
            elif event.name == "h":
                console.print(
                    "[bold yellow]нажата клавиша [bold white]h[/bold white][/bold yellow]"
                )
                return ActionKey.HELP
            elif event.name == "c":
                console.print(
                    "[bold yellow]нажата клавиша [bold white]c[/bold white][/bold yellow]"
                )
                return ActionKey.CATEGORY
            elif event.name == "i":
                console.print(
                    "[bold yellow]нажата клавиша [bold white]i[/bold white][/bold yellow]"
                )
                return ActionKey.INFO
            elif event.name == "d":
                console.print(
                    "[bold yellow]нажата клавиша [bold white]d[/bold white][/bold yellow]"
                )
                return ActionKey.DELETE_HISTORY
            elif event.name == "s":
                console.print(
                    "[bold yellow]нажата клавиша [bold white]s[/bold white][/bold yellow]"
                )
                return ActionKey.CONFIG_EDIT
        time.sleep(0.1)


def show_wallpaper_info(wallpaper: WallpaperHistory, index: int, total: int):
    info_text = f"""
    [bold cyan]Информация о текущих обоях:[/bold cyan]

    [bold yellow]Категория:[/bold yellow] {wallpaper.category}
    [bold yellow]URL:[/bold yellow] {wallpaper.url}
    [bold yellow]Локальный путь:[/bold yellow] {wallpaper.local_path}
    [bold yellow]Позиция в истории:[/bold yellow] {index + 1} из {total}
    """
    console.print(Panel(info_text, title="Информация", border_style="blue"))
    console.print("\n")
