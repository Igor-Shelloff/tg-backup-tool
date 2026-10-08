import os
import shutil
import PyInstaller.__main__

APP_NAME = "TGBackupTool"
MAIN_SCRIPT = "main.py"
ICON_FILE = "icon.ico" if os.path.exists("icon.ico") else None

print("Cleaning previous builds...")
for folder in ("build", "dist"):
    if os.path.exists(folder):
        shutil.rmtree(folder)

params = [
    f"--name={APP_NAME}",
    "--onefile",
    "--windowed",
    "--clean",
    "--noconfirm",
    "--add-data=app/locales;app/locales",
    "--collect-all=customtkinter",
    "--collect-data=customtkinter",
    "--collect-all=telethon",
    "--collect-all=qrcode",
    "--collect-all=cryptg",
    "--collect-all=PIL",
    "--hidden-import=PIL",
    "--hidden-import=PIL.Image",
    "--hidden-import=PIL.ImageTk",
    "--hidden-import=asyncio",
    "--hidden-import=tkinter",
    "--hidden-import=tkinter.ttk",
]

if ICON_FILE:
    params.append(f"--icon={ICON_FILE}")

params.append(MAIN_SCRIPT)

print("Building with PyInstaller...")
PyInstaller.__main__.run(params)

exe_path = os.path.join("dist", f"{APP_NAME}.exe" if os.name == "nt" else APP_NAME)
print(f"\nBuild complete: {exe_path}")