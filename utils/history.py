from dataclasses import asdict
import json
from os import path
import os
import sys
from config import history_file, logger
from models import WallpaperHistory
from utils.config_manager import ConfigKey, ConfigManager


class WallpaperHistoryManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

        # Получаем max_items из конфига
        self.max_items = self.config_manager.get_value(ConfigKey.MAX_ITEMS)

        self.history_file_path = history_file

        self.history = self.load_history()

    def load_history(self) -> list[WallpaperHistory | None]:
        if not path.exists(self.history_file_path):
            return []

        try:
            with open(self.history_file_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки истории: {e}")
            sys.exit(1)

        try:
            return [WallpaperHistory(**item) for item in history_data]
        except Exception as e:
            logger.error(f"Ошибка загрузки истории: {e}")
            sys.exit(1)

    def save_history(self):
        # Применяем лимит, обновляем значение max_items в случае изменений
        self.max_items = self.config_manager.get_value(ConfigKey.MAX_ITEMS)

        if len(self.history) > self.max_items:
            self.history = self.history[-self.max_items :]

        try:
            with open(self.history_file_path, "w", encoding="utf-8") as f:
                json.dump(
                    [asdict(item) for item in self.history],
                    f,
                    ensure_ascii=False,
                    indent=4,
                )
        except Exception as e:
            logger.error(f"Ошибка сохранения истории: {e}")
            sys.exit(1)

        logger.info(f"История сохранена: {self.history_file_path}")

    def add_entry(self, wallpaper: WallpaperHistory):
        if len(self.history) >= self.max_items:
            item = self.history.pop(0)
            if item.local_path:
                try:
                    os.remove(item.local_path)
                    logger.info(f"Удален файл: {item.local_path}")
                except Exception as e:
                    logger.error(f"Ошибка удаления файла: {e}")

        # Проверяем, есть ли уже запись с этим url
        if any(entry.url == wallpaper.url for entry in self.history):
            logger.info(f"Запись уже есть: {wallpaper.url}")
            return

        self.history.append(wallpaper)
        logger.info(f"Добавлена запись: {wallpaper}")

        self.save_history()

    def clear_history(self) -> []:
        if not self.history:
            logger.info("История уже пуста.")
            return

        for wallpaper in self.history:
            if wallpaper.local_path:
                try:
                    os.remove(wallpaper.local_path)
                    logger.info(f"Удален файл: {wallpaper.local_path}")
                except Exception as e:
                    logger.error(f"Ошибка удаления файла: {e}")

        self.history = []
        self.save_history()

    def get_history(self) -> list[WallpaperHistory | None]:
        return self.history
