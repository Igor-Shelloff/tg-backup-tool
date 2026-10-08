import sys
import os
import webbrowser

import customtkinter as ctk
from tkinter import messagebox

from app.ui.views.base import BaseView
from app.ui.theme import theme
from app.ui.components import PageHeader, SectionCard
from app.config import (
    APP_VERSION, DONATE_URL, GITHUB_URL, TELEGRAM_URL,
)


class SettingsView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._lang_map = {}
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        PageHeader(
            self,
            icon="⚙️",
            title=self.lang.get("settings_title"),
            subtitle=self.lang.get("settings_subtitle"),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        lang_card = SectionCard(self.scroll, title=self.lang.get("settings_language"))
        lang_card.grid(row=0, column=0, sticky="ew", pady=6, padx=4)
        lbody = lang_card.body()

        languages = self.lang.get_available_languages()
        self._lang_map = {name: code for code, name in languages}
        display_names = [name for _, name in languages]

        current_display = next(
            (name for code, name in languages if code == self.lang.current_lang),
            display_names[0] if display_names else "English",
        )
        self.lang_var = ctk.StringVar(value=current_display)

        ctk.CTkOptionMenu(
            lbody, values=display_names,
            variable=self.lang_var, width=240,
        ).grid(row=0, column=0, sticky="w", pady=6)

        ctk.CTkLabel(
            lbody,
            text=self.lang.get("settings_restart_message").split("\n")[0],
            font=ctk.CTkFont(size=10),
            text_color=theme.fg_muted,
        ).grid(row=1, column=0, sticky="w", pady=(0, 6))

        appear_card = SectionCard(self.scroll, title=self.lang.get("settings_appearance"))
        appear_card.grid(row=1, column=0, sticky="ew", pady=6, padx=4)
        abody = appear_card.body()

        self.appear_var = ctk.StringVar(value=self.app.config.get("appearance", "Dark"))
        opts = [
            ("settings_appearance_system", "System"),
            ("settings_appearance_light", "Light"),
            ("settings_appearance_dark", "Dark"),
        ]
        row = ctk.CTkFrame(abody, fg_color="transparent")
        row.grid(row=0, column=0, sticky="w")
        for label_key, value in opts:
            ctk.CTkRadioButton(
                row, text=self.lang.get(label_key),
                variable=self.appear_var, value=value,
            ).pack(side="left", padx=8, pady=6)

        ctk.CTkLabel(
            abody,
            text=self.lang.get("settings_restart_message").split("\n")[0],
            font=ctk.CTkFont(size=10),
            text_color=theme.fg_muted,
        ).grid(row=1, column=0, sticky="w", pady=(0, 6))

        save_card = SectionCard(self.scroll)
        save_card.grid(row=2, column=0, sticky="ew", pady=6, padx=4)
        sbody = save_card.body()

        ctk.CTkButton(
            sbody, text=self.lang.get("settings_save"),
            command=self._save_settings,
            width=220, height=42,
            fg_color=theme.accent, hover_color="#1f5580",
        ).grid(row=0, column=0, sticky="w", pady=6)

        about_card = SectionCard(self.scroll, title=self.lang.get("settings_about"))
        about_card.grid(row=3, column=0, sticky="ew", pady=6, padx=4)
        obody = about_card.body()

        ctk.CTkLabel(
            obody,
            text=f"Telegram Backup Tool v{APP_VERSION}\nOpen Source Project",
            justify="left", anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        btn_row = ctk.CTkFrame(obody, fg_color="transparent")
        btn_row.grid(row=1, column=0, sticky="w")

        ctk.CTkButton(
            btn_row, text=self.lang.get("settings_donate"),
            command=lambda: webbrowser.open(DONATE_URL),
            fg_color="#e63946", hover_color="#d62828",
            width=200,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text=self.lang.get("settings_github"),
            command=lambda: webbrowser.open(GITHUB_URL),
            fg_color="#333333", hover_color="#555555",
            width=200,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text=self.lang.get("settings_telegram"),
            command=lambda: webbrowser.open(TELEGRAM_URL),
            fg_color="#2b719e", hover_color="#1f5580",
            width=200,
        ).pack(side="left", padx=8)

    def _save_settings(self):
        new_lang = self._lang_map.get(self.lang_var.get(), "en")
        new_appear = self.appear_var.get()

        old_lang = self.lang.current_lang
        old_appear = self.app.config.get("appearance", "Dark")

        self.app.config["appearance"] = new_appear
        self.lang.save_language_preference(new_lang)
        self.app.save_settings()

        restart_needed = (new_lang != old_lang) or (new_appear != old_appear)

        if restart_needed:
            answer = messagebox.askyesno(
                self.lang.get("settings_restart_title"),
                self.lang.get("settings_restart_message"),
                parent=self,
            )
            if answer:
                self._restart_app()
        else:
            messagebox.showinfo(
                self.lang.get("status_ok"),
                self.lang.get("settings_saved"),
                parent=self,
            )

    def _restart_app(self):
        import subprocess
        import sys

        if getattr(sys, "frozen", False):
            subprocess.Popen([sys.executable])
        else:
            subprocess.Popen([sys.executable, "main.py"])

        try:
            self.app.on_close()
        except Exception:
            pass
        sys.exit(0)

    def on_show(self):
        pass

    def on_state_changed(self):
        pass