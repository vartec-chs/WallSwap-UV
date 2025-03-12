import logging
from os import path
from rich.console import Console
from rich.logging import RichHandler
from appdirs import user_config_dir

console = Console()

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[RichHandler(console=console)],
)

logger = logging.getLogger(__name__)

APP_NAME = "WallSwap UV"
APP_AUTHOR = "Vartec"

config_dir = user_config_dir(APP_NAME, APP_AUTHOR)
config_file = path.join(config_dir, "config.json")
cache_dir = path.join(config_dir, "Cache")
history_file = path.join(config_dir, "history.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.0.0 Safari/537.36"
}
