import json
from os import path

from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from config import config_file, logger, console
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, Type, TypeVar


@dataclass
class AppConfig:
    max_items: int = 50
    # theme: str = "light"
    # language: str = "en"
    # добавляешь новые поля здесь:
    # download_folder: Optional[str] = None


class ConfigKey(Enum):
    MAX_ITEMS = "max_items"
    # THEME = 'theme'
    # LANGUAGE = 'language'
    # DOWNLOAD_FOLDER = 'download_folder'
    # ENABLE_NOTIFICATIONS = 'enable_notifications'


T = TypeVar("T")


class ConfigManager:
    def __init__(self, config_class: Type[T] = AppConfig):
        self.config_class = config_class

        # Путь к файлу конфигурации
        self.config_file_path = config_file

        # Загружаем или создаем дефолтный конфиг
        self.config: T = self.load_config()

    def load_config(self) -> T:
        if not path.exists(self.config_file_path):
            logger.warning("Файл конфига не найден. Создаем дефолтный.")
            config_instance = self.config_class()
            self.save_config(config_instance)
            self.create_config_interactive(config_instance)
            return config_instance

        try:
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфига: {e}")
            return

        # Создаем экземпляр конфигурации с данными из файла
        config_instance = self.config_class(**data)

        return config_instance

    def save_config(self, config: Optional[T] = None):
        if config is None:
            config = self.config

        try:
            with open(self.config_file_path, "w", encoding="utf-8") as f:
                json.dump(asdict(config), f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Ошибка при сохранении конфига: {e}")
            return

        logger.info(f"Конфиг сохранен: {self.config_file_path}")

    def get(self) -> T:
        """Получить весь конфиг"""
        return self.config

    def update(self, **kwargs):
        """Обновить один или несколько параметров"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Параметр {key} обновлен: {value}")
            else:
                logger.warning(f"Параметр {key} не существует в конфиге")

        self.save_config()

    def get_value(self, key: ConfigKey) -> any:
        return getattr(self.config, key.value)

    def set_value(self, key: str, value):
        """Установить конкретный параметр по ключу"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            logger.info(f"Параметр {key} установлен: {value}")
            self.save_config()
        else:
            logger.warning(f"Параметр {key} не существует в конфиге")

    def create_config_interactive(self, config_instance: T):
        """Интерактивный опрос для создания конфига"""

        console.rule("Пожалуйста, настройте параметры конфигурации:")

        # Опрашиваем пользователя на ввод каждого параметра
        config_instance.max_items = IntPrompt.ask(
            "\n[bold]Максимальное количество записей в истории[/bold]", default=50
        )
        # self.config.theme = Prompt.ask("Тема приложения", choices=["light", "dark"], default="light")
        # self.config.language = Prompt.ask("Язык приложения", choices=["en", "ru"], default="en")
        # self.config.enable_notifications = Confirm.ask("Включить уведомления?", default=True)

        self.save_config(config_instance)
        console.print("Конфиг успешно создан и сохранен.")

    def edit_config_interactive(self):
        """Интерактивное меню редактирования конфига"""

        # Список доступных параметров
        options = {
            "max_items": "Максимальное количество записей в истории",
            # "theme": "Тема приложения",
            # "language": "Язык приложения",
            # "enable_notifications": "Включить уведомления"
        }

        text = "\n".join(
            [
                f"{i}. {description}"
                for i, (key, description) in enumerate(options.items(), 1)
            ]
        )

        console.print("\n")
        # Печатаем список опций
        console.print(
            Panel(
                text,
                title="Редактирование конфигурации",
                border_style="green",
                padding=(1, 2),
            )
        )

        while True:
            choice = IntPrompt.ask(
                "\nВведите номер параметра для редактирования",
                choices=[str(i) for i in range(1, len(options) + 1)],
                default=1,
                show_choices=False,
            )
            if choice in range(1, len(options) + 1):
                break
            else:
                console.print("[bold red]Ошибка: Неверный номер параметра.[/bold red]")

        # Получаем ключ, выбранный пользователем
        selected_key = list(options.keys())[choice - 1]
        current_value = getattr(self.config, selected_key)

        if selected_key == "max_items":
            new_value = IntPrompt.ask(
                f"\n{options[selected_key]} (текущее: {current_value})",
                default=current_value,
            )
        elif selected_key == "theme":
            new_value = Prompt.ask(
                f"\n{options[selected_key]} (текущее: {current_value})",
                choices=["light", "dark"],
                default=current_value,
            )
        elif selected_key == "language":
            new_value = Prompt.ask(
                f"{options[selected_key]} (текущее: {current_value})",
                choices=["en", "ru"],
                default=current_value,
            )
        elif selected_key == "enable_notifications":
            new_value = Confirm.ask(
                f"{options[selected_key]} (текущее: {current_value})",
                default=current_value,
            )

        # Обновляем конфиг
        setattr(self.config, selected_key, new_value)
        self.save_config()
        console.print(
            f"\n[bold cyan]{options[selected_key]}[/bold cyan] обновлен на [bold cyan]{new_value}[/bold cyan]\n"
        )
