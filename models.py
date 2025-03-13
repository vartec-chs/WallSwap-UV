from dataclasses import dataclass


@dataclass
class Category:
    name: str
    url: str


@dataclass
class WallpaperHistory:
    url: str
    local_path: str
    category: str
