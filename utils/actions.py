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


options = {
    "shift": {
        "name": "shift",
        "alias": ["right shift", "left shift"],
        "action": ActionKey.NEXT,
        "description": "Загрузить следующие обои",
    },
    "backspace": {
        "name": "backspace",
        "action": ActionKey.PREVIOUS,
        "description": "Вернуться к предыдущим обоям",
    },
    "esc": {
        "name": "esc",
        "action": ActionKey.EXIT,
        "description": "Выйти из программы",
    },
    "h": {
        "name": "h",
        "action": ActionKey.HELP,
        "description": "Показать эту справку",
    },
    "c": {
        "name": "c",
        "action": ActionKey.CATEGORY,
        "description": "Изменить категорию обоев",
    },
    "i": {
        "name": "i",
        "action": ActionKey.INFO,
        "description": "Показать информацию о текущих обоях",
    },
    "d": {
        "name": "d",
        "action": ActionKey.DELETE_HISTORY,
        "description": "Удалить историю обоев",
    },
    "s": {
        "name": "s",
        "action": ActionKey.CONFIG_EDIT,
        "description": "Отредактировать конфигурацию",
    },
}


def show_help():
    console.print("\n")
    help_text = "\n".join(
        [
            f"[bold yellow]{key}[/bold yellow] - {options[key]['description']}"
            for key in options
        ]
    )
    console.print(
        Panel(help_text, title="[bold]Доступные команды[/bold]", border_style="green")
    )


def wait_for_key_press() -> ActionKey:
    show_help()
    console.print("\n[bold]Нажмите клавишу из списка:[/bold]", end=" ")
    while True:
        event = keyboard.read_event()
        if event.event_type == "down":
            if event.name in options:
                pressed_key_print(event.name)
                return options[event.name]["action"]
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


def pressed_key_print(key_name: str):
    console.print(
        f"[bold yellow]нажата клавиша [underline]{key_name}[/underline][/bold yellow]"
    )
