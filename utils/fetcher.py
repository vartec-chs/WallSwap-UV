import requests
from config import logger, HEADERS

def fetch(url: str) -> requests.Response | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к {url}: {e}")
        return None