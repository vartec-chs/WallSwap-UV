import sys

from utils.clear_cmd import clear_cmd
from config import console, logger
from utils.config_manager import ConfigManager
from utils.history_manager import WallpaperHistoryManager
from wall_swapper import WallSwapper


def main():
    clear_cmd()
    config_manager_instance = ConfigManager()
    history_manager_instance = WallpaperHistoryManager(config_manager_instance)
    wall_swapper = WallSwapper(
        sys.argv[1:], config_manager_instance, history_manager_instance
    )
    try:
        wall_swapper.run()
    except KeyboardInterrupt:
        console.print("\n")
        logger.error("Ошибка: Прерывание программы пользователем")
        sys.exit(1)


if __name__ == "__main__":
    main()
