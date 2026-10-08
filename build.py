import os
import shutil
import PyInstaller.__main__

APP_NAME = "TGBackupTool"
MAIN_SCRIPT = "main.py"
ICON_FILE = "icon.ico" if os.name == "nt" and os.path.exists("icon.ico") else None

SEP = ";" if os.name == "nt" else ":"

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

if os.name != "nt":
    params.append("--collect-all=cryptg")

if ICON_FILE:
    params.append(f"--icon={ICON_FILE}")

params.append(MAIN_SCRIPT)

print("Building with PyInstaller...")
PyInstaller.__main__.run(params)

exe_path = os.path.join("dist", f"{APP_NAME}.exe" if os.name == "nt" else APP_NAME)
print(f"\nBuild complete: {exe_path}")