import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

from app.ui.views.base import BaseView
from app.ui.theme import theme
from app.ui.components import PageHeader


class LogView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        PageHeader(
            self,
            icon="📜",
            title=self.lang.get("log_title"),
            subtitle=self.lang.get("log_subtitle"),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.text = ctk.CTkTextbox(
            self, wrap="word",
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.text.grid(row=1, column=0, sticky="nsew", pady=(0, 8))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=2, column=0, sticky="ew")

        ctk.CTkButton(btns, text=self.lang.get("log_clear"),
                      command=self._clear, width=140).pack(side="left", padx=2)
        ctk.CTkButton(btns, text=self.lang.get("log_copy"),
                      command=self._copy, width=160).pack(side="left", padx=2)
        ctk.CTkButton(btns, text=self.lang.get("log_save"),
                      command=self._save, width=160).pack(side="left", padx=2)

        self.silent_var = ctk.BooleanVar(value=self.app.config.get("silent_log", True))
        ctk.CTkCheckBox(
            btns, text=self.lang.get("log_silent"),
            variable=self.silent_var,
            command=self._on_silent_toggle,
        ).pack(side="right", padx=6)

    def append_line(self, message):
        self.text.configure(state="normal")
        self.text.insert("end", message + "\n")
        self.text.see("end")
        self.text.configure(state="disabled")

    def _clear(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

    def _copy(self):
        content = self.text.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(content)

    def _save(self):
        content = self.text.get("1.0", "end").strip()
        if not content:
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt")],
            initialfile=f"log_{ts}.txt",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo(
                self.lang.get("status_ok"), path, parent=self,
            )
        except Exception as e:
            messagebox.showerror(self.lang.get("error"), str(e), parent=self)

    def _on_silent_toggle(self):
        self.app.config["silent_log"] = self.silent_var.get()
        self.app.save_settings()

    def on_show(self):
        pass

    def on_state_changed(self):
        pass