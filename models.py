from dataclasses import dataclass


@dataclass
class Category:
    name: str
    url: str


@dataclass
class WallpaperHistory:
    # timestamp: int
    url: str
    local_path: str
    category: str
