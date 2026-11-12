import os
import sys
from pathlib import Path

# запущено из собранного exe/app (PyInstaller)
frozen = getattr(sys, "frozen", False)


def resource_dir():
    """Папка с ресурсами (шрифты, карта, иконка): рядом с проектом или внутри сборки."""
    if frozen:
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def writable_dir():
    """Папка, куда можно писать (база, результаты, готовая карта).

    Из исходников это папка проекта, из exe/app — папка данных пользователя,
    потому что внутри сборки писать нельзя, а временная папка onefile стирается при выходе.
    """
    if not frozen:
        return resource_dir()

    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home())))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    folder = base / "kanash-oil-status"
    folder.mkdir(parents=True, exist_ok=True)
    return folder
