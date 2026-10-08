import os
import shutil
import sys
import PyInstaller.__main__

APP_NAME = "TGBackupTool"
MAIN_SCRIPT = "main.py"
SEP = ";" if os.name == "nt" else ":"

if sys.platform == "win32":
    ICON_FILE = "icon.ico" if os.path.exists("icon.ico") else None
elif sys.platform == "darwin":
    ICON_FILE = "icon.icns" if os.path.exists("icon.icns") else None
else:
    ICON_FILE = None

print("Cleaning previous builds...")
for folder in ("build", "dist"):
    if os.path.exists(folder):
        shutil.rmtree(folder)

params = [
    f"--name={APP_NAME}",
    "--windowed",
    "--clean",
    "--noconfirm",
    f"--add-data=app/locales{SEP}app/locales",
    "--collect-all=customtkinter",
    "--collect-data=customtkinter",
    "--collect-all=telethon",
    "--collect-all=qrcode",
    "--collect-all=PIL",
    "--hidden-import=PIL",
    "--hidden-import=PIL.Image",
    "--hidden-import=PIL.ImageTk",
    "--hidden-import=asyncio",
    "--hidden-import=tkinter",
    "--hidden-import=tkinter.ttk",
]

if sys.platform == "win32":
    params.append("--onefile")
elif sys.platform == "darwin":
    params.append("--collect-all=cryptg")
else:
    params.append("--collect-all=cryptg")

if ICON_FILE:
    params.append(f"--icon={ICON_FILE}")

params.append(MAIN_SCRIPT)

print("Building with PyInstaller...")
PyInstaller.__main__.run(params)

if sys.platform == "darwin":
    print(f"\nBuild complete: dist/{APP_NAME}.app")
elif sys.platform == "win32":
    print(f"\nBuild complete: dist/{APP_NAME}.exe")
else:
    print(f"\nBuild complete: dist/{APP_NAME}")