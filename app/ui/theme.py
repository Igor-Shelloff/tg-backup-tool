import customtkinter as ctk


class _Theme:
    def __init__(self):
        self.refresh()

    def refresh(self):
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            self.bg = "#1a1a1a"
            self.card = "#242424"
            self.card_hover = "#2f2f2f"
            self.border = "#3a3a3a"
            self.fg = "#ffffff"
            self.fg_muted = "#9a9a9a"
            self.ok = "#2ecc71"
            self.warn = "#f39c12"
            self.error = "#e74c3c"
            self.info = "#3498db"
            self.accent = "#2b719e"
        else:
            self.bg = "#f5f5f5"
            self.card = "#ffffff"
            self.card_hover = "#eaeaea"
            self.border = "#d0d0d0"
            self.fg = "#1a1a1a"
            self.fg_muted = "#6a6a6a"
            self.ok = "#27ae60"
            self.warn = "#e67e22"
            self.error = "#c0392b"
            self.info = "#2980b9"
            self.accent = "#2b719e"


theme = _Theme()