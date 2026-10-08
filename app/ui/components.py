from typing import Callable, Optional
import customtkinter as ctk
from app.ui.theme import theme


class PageHeader(ctk.CTkFrame):
    def __init__(self, master, icon, title, subtitle=None,
                 action_text=None, action_command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text=icon, font=ctk.CTkFont(size=26),
        ).grid(row=0, column=0, rowspan=2, padx=(0, 12), sticky="w")

        ctk.CTkLabel(
            self, text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        if subtitle:
            ctk.CTkLabel(
                self, text=subtitle,
                font=ctk.CTkFont(size=11),
                text_color=theme.fg_muted,
                anchor="w",
            ).grid(row=1, column=1, sticky="w", pady=(2, 0))

        if action_text and action_command:
            ctk.CTkButton(
                self, text=action_text, command=action_command,
                width=180, height=36,
            ).grid(row=0, column=2, rowspan=2, padx=(12, 0), sticky="e")


class EmptyState(ctk.CTkFrame):
    def __init__(self, master, icon, title, hint,
                 button_text=None, command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.grid(row=0, column=0)

        ctk.CTkLabel(inner, text=icon, font=ctk.CTkFont(size=64)).pack(pady=(0, 16))
        ctk.CTkLabel(
            inner, text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.fg,
        ).pack(pady=(0, 8))
        ctk.CTkLabel(
            inner, text=hint,
            font=ctk.CTkFont(size=12),
            text_color=theme.fg_muted,
            wraplength=420, justify="center",
        ).pack(pady=(0, 24))

        if button_text and command:
            ctk.CTkButton(
                inner, text=button_text, command=command,
                width=220, height=42,
                font=ctk.CTkFont(size=13, weight="bold"),
            ).pack()


class SectionCard(ctk.CTkFrame):
    def __init__(self, master, title=None, **kwargs):
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self._row = 0

        if title:
            ctk.CTkLabel(
                self, text=title,
                font=ctk.CTkFont(weight="bold"),
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))
            self._row = 1

    def body(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=self._row, column=0, sticky="ew", padx=12, pady=(0, 12))
        frame.grid_columnconfigure(0, weight=1)
        return frame