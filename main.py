import customtkinter as ctk

from app.ui.main_window import MainWindow


def main():
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()