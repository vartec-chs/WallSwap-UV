import os
import sys
import time


from config import console, logger, cache_dir
from models import Category, WallpaperHistory

from utils.categories import get_categories, show_categories
from utils.wallpapers import get_random_wallpaper, download_wallpaper, set_wallpaper
from utils.actions import ActionKey, show_help, wait_for_key_press, show_wallpaper_info
from utils.config_manager import ConfigManager
from utils.history_manager import WallpaperHistoryManager
from utils.clear_cmd import clear_cmd

from rich.prompt import Prompt, Confirm


class WallSwapper:
    def __init__(
        self,
        sys_params: list[str],
        config_manager: ConfigManager,
        history_manager: WallpaperHistoryManager,
    ):
        self.config_manager = config_manager
        self.history_manager = history_manager
        self.cache_dir = cache_dir
        self.categories: list[Category] | None = None
        self.select_category: Category | None = None
        self.current_index: int = len(self.history_manager.get_history()) - 1
        self.sys_choice: str | None = None
        self.sys_params: list[str] | None = sys_params

    def __load_categories(self):
        self.categories = get_categories()
        if not self.categories:
            logger.error("Категории не найдены!")
            sys.exit(1)
        self.select_category = self.categories[0]

    def __show_categories(self):
        clear_cmd()
        show_categories(self.categories)

    def __choice_category(self):
        clear_cmd()
        self.__show_categories()
        while True:
            new_choice = Prompt.ask(
                "\n[bold white]Введите номер категории или ([blink]0[/blink]) для выхода[/bold white]",
                choices=[str(i) for i in range(1, len(self.categories) + 1)] + ["0"],
                default="0",
                show_choices=False,
            )

            if new_choice.isnumeric() and int(new_choice) in range(
                1, len(self.categories) + 1
            ):
                self.select_category = self.categories[int(new_choice) - 1]
                clear_cmd()
                console.print(
                    f"\n[bold green]✅ Выбрана категория: [bold cyan]{self.select_category.name}[/bold cyan]",
                    end="",
                )
                break
            elif new_choice.isnumeric() and int(new_choice) == 0:
                console.print("\n[bold green]✅ Вы вышли![/bold green]\n")
                sys.exit(0)
            else:
                console.print(
                    "[bold red]Ошибка: Введите число в пределах списка.[/bold red]"
                )

    def __next_wallpaper(self):
        clear_cmd()
        if not self.select_category:
            console.print("\n[bold red]❌ Вы не выбрали категорию![/bold red]", end="")
            return
        wallpaper_url = get_random_wallpaper(self.select_category.url, self.select_category.name)
        if not wallpaper_url:
            retry = Confirm.ask("[bold yellow]Попробовать еще раз?[/bold yellow]")
            if not retry:
                return
            self.__next_wallpaper()
        timestamp = int(time.time())
        save_path = os.path.join(cache_dir, f"wallpaper_{timestamp}.jpg")
        if download_wallpaper(wallpaper_url, save_path):
            set_wallpaper(save_path)
            self.history_manager.add_entry(
                WallpaperHistory(wallpaper_url, save_path, self.select_category.name)
            )
            self.current_index = len(self.history_manager.get_history()) - 1

    def __previous_wallpaper(self):
        clear_cmd()
        if self.current_index > 0:
            self.current_index -= 1
            previous = self.history_manager.get_history()[self.current_index]
            show_wallpaper_info(
                previous,
                self.current_index,
                len(self.history_manager.get_history()),
            )
            set_wallpaper(previous.local_path)
        else:
            console.print("\n\n[bold red]❌ Нет предыдущих обоев в истории.[/bold red]")

    def __info_wallpaper(self):
        clear_cmd()
        if self.current_index >= 0:
            show_wallpaper_info(
                self.history_manager.get_history()[self.current_index],
                self.current_index,
                len(self.history_manager.get_history()),
            )
        else:
            console.print("\n\n[bold red]❌ Нет информации об обоях.[/bold red]")

    def __edit_config(self):
        clear_cmd()
        self.config_manager.edit_config_interactive()

    def __delete_history(self):
        clear_cmd()
        self.history_manager.clear_history()
        self.current_index = -1
        console.print("\n\n[bold green]✅ Обои удалены![/bold green]")

    def __args_handler(self):
        pass

    def __choice_handler(self):
        pass

    def run(self):
        clear_cmd()
        self.__args_handler()
        self.__load_categories()

        while True:
            action = wait_for_key_press()
            match action:
                case ActionKey.NEXT:
                    self.__next_wallpaper()
                case ActionKey.PREVIOUS:
                    self.__previous_wallpaper()
                case ActionKey.HELP:
                    show_help()
                case ActionKey.DELETE_HISTORY:
                    self.__delete_history()
                case ActionKey.INFO:
                    self.__info_wallpaper()
                case ActionKey.CATEGORY:
                    self.__choice_category()
                case ActionKey.CONFIG_EDIT:
                    self.__edit_config()
                case ActionKey.EXIT:
                    sys.exit(0)