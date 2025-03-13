import os
import subprocess

SCRIPT_NAME = "main.py"
EXE_NAME = "WallSwap UV"
ICON_PATH = "icon.ico"


try:
    import PyInstaller
except ImportError:
    print("PyInstaller не найден, устанавливаю...")
    subprocess.run(["pip", "install", "pyinstaller"], check=True)

cmd = [
    "pyinstaller",
    "--onefile",
    f"--name={EXE_NAME}",
    f"--icon={ICON_PATH}",
    SCRIPT_NAME,
]


print("Сборка началась...")
subprocess.run(cmd, check=True)


print("Очистка временных файлов...")
for folder in ["build", "__pycache__"]:
    if os.path.exists(folder):
        os.system(f"rmdir /s /q {folder}")  # Для Windows

print(f"Сборка завершена! Файл находится в папке dist/{EXE_NAME}.exe")
