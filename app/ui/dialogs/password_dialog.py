import customtkinter as ctk

from app.ui.context_menu import attach_context_menu


class PasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, lang, callback):
        super().__init__(parent)
        self.lang = lang
        self.callback = callback
        self._sent = False

        self.title(lang.get("password_title"))
        self.geometry("380x220")
        self.resizable(False, False)
        self.transient(parent)
        try:
            self.grab_set()
        except Exception:
            pass

        ctk.CTkLabel(
            self, text=lang.get("password_title"),
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(20, 6))

        ctk.CTkLabel(
            self, text=lang.get("password_hint"),
            font=ctk.CTkFont(size=11), wraplength=320, justify="center",
        ).pack(pady=(0, 12))

        self.entry = ctk.CTkEntry(
            self, width=240, show="*",
            placeholder_text=lang.get("password_label"),
        )
        self.entry.pack(pady=6)
        self.entry.bind("<Return>", lambda e: self._confirm())
        attach_context_menu(self.entry, lang)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(pady=14)

        ctk.CTkButton(
            btns, text=lang.get("password_confirm"),
            command=self._confirm, width=120,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btns, text=lang.get("password_cancel"),
            command=self._cancel, width=120,
            fg_color="transparent", border_width=1,
        ).pack(side="left", padx=6)

        self.after(100, self.entry.focus_set)

    def _confirm(self):
        if self._sent:
            return
        self._sent = True
        pwd = self.entry.get()
        try:
            self.destroy()
        except Exception:
            pass
        self.callback(pwd)

    def _cancel(self):
        if self._sent:
            return
        self._sent = True
        try:
            self.destroy()
        except Exception:
            pass
        self.callback(None)