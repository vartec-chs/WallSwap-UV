import os
import sys
import time


from config import console, logger, config_dir, cache_dir
from models import WallpaperHistory

from utils.categories import get_categories, show_categories
from utils.wallpapers import get_random_wallpaper, download_wallpaper, set_wallpaper
from utils.actions import ActionKey, show_help, wait_for_key_press, show_wallpaper_info
from utils.config_manager import ConfigManager
from utils.history import WallpaperHistoryManager

from rich.prompt import Prompt, Confirm


def main():
    os.system("cls")
    os.makedirs(config_dir, exist_ok=True)
    config = ConfigManager()
    history_manager = WallpaperHistoryManager(config)
    os.makedirs(cache_dir, exist_ok=True)
    os.system("cls")
    console.rule("[bold blue]Папка конфигурации:[/bold blue]")
    console.print(f"[bold cyan]{config_dir}[/bold cyan]")

    current_index = -1

    sys_choice = sys.argv[1] if len(sys.argv) > 1 else None
    categories = get_categories()

    if not categories:
        logger.error("Категории не найдены!")
        return

    if not sys_choice:
        show_categories(categories)
    elif sys_choice in ["-c", "--categories", "--list"]:
        return show_categories(categories)

    choice = None
    try:
        if sys_choice:
            if sys_choice.isnumeric() and int(sys_choice) in range(
                1, len(categories) + 1
            ):
                choice = int(sys_choice) - 1
            elif sys_choice.isnumeric() and int(sys_choice) == 0:
                return console.print("\n[bold green]✅ Вы вышли![/bold green]")
            else:
                return console.print(
                    "[bold red]Ошибка: Введите число в пределах списка.[/bold red]"
                )
        else:
            while True:
                choice = Prompt.ask(
                    "\n[bold green]Введите номер категории или ([blink]0[/blink]) для выхода[/bold green]"
                )
                if choice.isnumeric() and int(choice) in range(1, len(categories) + 1):
                    choice = int(choice) - 1
                    break
                elif choice.isnumeric() and int(choice) == 0:
                    return console.print("\n[bold green]✅ Вы вышли![/bold green]")
                else:
                    console.print(
                        "[bold red]Ошибка: Введите число в пределах списка.[/bold red]"
                    )
    except ValueError:
        console.print("[bold red]Неверный ввод. Введите число![/bold red]")
        return

    category = categories[choice]

    while True:
        wallpaper_history = history_manager.get_history()
        console.print(
            f"[bold magenta]\nЗагружаем обои из категории:[/bold magenta] [cyan]{category.name}[/cyan]"
        )
        wallpaper_url = get_random_wallpaper(category.url)
        if not wallpaper_url:
            retry = Confirm.ask("[bold yellow]Попробовать еще раз?[/bold yellow]")
            if not retry:
                return
            continue

        timestamp = int(time.time())
        save_path = os.path.join(cache_dir, f"wallpaper_{timestamp}.jpg")

        if download_wallpaper(wallpaper_url, save_path):
            set_wallpaper(save_path)
            history_manager.add_entry(
                WallpaperHistory(wallpaper_url, save_path, category.name)
            )
            current_index = len(wallpaper_history) - 1

            while True:
                action = wait_for_key_press()

                if action == ActionKey.EXIT:
                    return

                elif action == ActionKey.PREVIOUS:
                    if current_index > 0:
                        current_index -= 1
                        previous = wallpaper_history[current_index]
                        show_wallpaper_info(
                            previous, current_index, len(wallpaper_history)
                        )
                        set_wallpaper(previous.local_path)
                    else:
                        console.print(
                            "\n\n[bold red]❌ Нет предыдущих обоев в истории.[/bold red]\n\n"
                        )

                elif action == ActionKey.HELP:
                    show_help()

                elif action == ActionKey.DELETE_HISTORY:
                    wallpaper_history = history_manager.clear_history()
                    current_index = -1
                    console.print("\n\n[bold green]✅ Обои удалены![/bold green]\n\n")

                elif action == ActionKey.INFO:
                    if current_index >= 0:
                        show_wallpaper_info(
                            wallpaper_history[current_index],
                            current_index,
                            len(wallpaper_history),
                        )
                    else:
                        console.print(
                            "\n\n[bold red]Нет информации об обоях.[/bold red]\n\n"
                        )

                elif action == ActionKey.CATEGORY:
                    show_categories(categories)
                    while True:
                        new_choice = Prompt.ask(
                            "\n[bold green]Введите номер категории или ([blink]0[/blink]) для выхода[/bold green]"
                        )
                        if new_choice.isnumeric() and int(new_choice) in range(
                            1, len(categories) + 1
                        ):
                            category = categories[int(new_choice) - 1]
                            console.print(
                                f"\n[bold green]✅ Выбрана категория: [bold cyan]{category.name}[/bold cyan]\n"
                            )
                            break
                        elif new_choice.isnumeric() and int(new_choice) == 0:
                            console.print("\n[bold green]✅ Вы вышли![/bold green]\n")
                            return sys.exit(0)
                        else:
                            console.print(
                                "[bold red]Ошибка: Введите число в пределах списка.[/bold red]"
                            )

                elif action == ActionKey.CONFIG_EDIT:
                    config.edit_config_interactive()

                elif action == ActionKey.NEXT:
                    break
        else:
            retry = Confirm.ask("[bold yellow]Попробовать еще раз?[/bold yellow]")
            if not retry:
                break


if __name__ == "__main__":
    main()
