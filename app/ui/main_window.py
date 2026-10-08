import json

import customtkinter as ctk

from app.config import APP_VERSION, SETTINGS_FILE, DEFAULT_SETTINGS
from app.core.language_manager import LanguageManager
from app.core.telegram_client import TelegramBackupClient
from app.ui.theme import theme
from app.ui.context_menu import attach_context_menu_recursive
from app.ui.views.auth import AuthView
from app.ui.views.export import ExportView
from app.ui.views.import_ import ImportView
from app.ui.views.log import LogView
from app.ui.views.settings import SettingsView
from app.ui.dialogs.qr_dialog import QRDialog
from app.ui.dialogs.code_dialog import CodeDialog
from app.ui.dialogs.password_dialog import PasswordDialog


VIEW_CLASSES = {
    "auth":     (AuthView,     "🔐"),
    "export":   (ExportView,   "📤"),
    "import":   (ImportView,   "📥"),
    "log":      (LogView,      "📜"),
    "settings": (SettingsView, "⚙️"),
}

VIEW_GROUPS = [
    ("sidebar_group_main",   ["auth", "export", "import"]),
    ("sidebar_group_system", ["log", "settings"]),
]


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.lang = LanguageManager()
        self.config = self._load_config()

        ctk.set_appearance_mode(self.config.get("appearance", "Dark"))
        theme.refresh()

        self.root.title(self.lang.get("app_title") + f" v{APP_VERSION}")
        self.root.geometry("1180x780")
        self.root.minsize(960, 640)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.client = TelegramBackupClient(self)
        self.is_authorized = False
        self.user_info = ""
        self.auth_in_progress = False
        self.qr_window = None
        self._active_view = None
        self.views = {}
        self._menu_buttons = {}

        self._build_ui()
        self.show_view("auth")

    def _load_config(self):
        cfg = DEFAULT_SETTINGS.copy()
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    cfg.update(json.load(f))
            except Exception:
                pass
        return cfg

    def save_settings(self):
        try:
            data = {}
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            data["appearance"] = self.config.get("appearance", "Dark")
            data["silent_log"] = self.config.get("silent_log", True)
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _build_ui(self):
        self.sidebar = ctk.CTkFrame(self.root, width=230, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="⚡ TG Backup",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 2), padx=16, anchor="w")

        ctk.CTkLabel(
            self.sidebar, text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=10), text_color=theme.fg_muted,
        ).pack(pady=(0, 12), padx=16, anchor="w")

        self._menu_buttons.clear()
        for group_key, keys in VIEW_GROUPS:
            ctk.CTkLabel(
                self.sidebar,
                text=self.lang.get(group_key).upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=theme.fg_muted,
                anchor="w",
            ).pack(fill="x", padx=20, pady=(12, 4))

            for key in keys:
                if key not in VIEW_CLASSES:
                    continue
                icon = VIEW_CLASSES[key][1]
                btn = ctk.CTkButton(
                    self.sidebar,
                    text=f"  {icon}  {self.lang.get('view_' + key)}",
                    command=lambda k=key: self.show_view(k),
                    anchor="w", height=38, corner_radius=8,
                    fg_color="transparent",
                    hover_color=theme.card_hover,
                    text_color=theme.fg,
                )
                btn.pack(fill="x", padx=10, pady=2)
                self._menu_buttons[key] = btn

        status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        status_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        self.status_label = ctk.CTkLabel(
            status_frame, text=self.lang.get("status_ready"),
            font=ctk.CTkFont(size=10),
            text_color=theme.fg_muted, wraplength=200, justify="left",
        )
        self.status_label.pack(anchor="w")

        self.content = ctk.CTkFrame(self.root, corner_radius=0, fg_color=theme.bg)
        self.content.pack(side="right", fill="both", expand=True)

        self.views.clear()
        for key, (Cls, _) in VIEW_CLASSES.items():
            self.views[key] = Cls(self.content, self)

        attach_context_menu_recursive(self.content, self.lang)

    def show_view(self, key):
        if key not in self.views:
            return
        if self._active_view:
            old = self.views.get(self._active_view)
            if old and hasattr(old, "on_hide"):
                old.on_hide()
            if old:
                old.pack_forget()
            if self._active_view in self._menu_buttons:
                self._menu_buttons[self._active_view].configure(fg_color="transparent")

        view = self.views[key]
        view.pack(fill="both", expand=True, padx=12, pady=12)
        self._menu_buttons[key].configure(fg_color=theme.card_hover)
        self._active_view = key
        if hasattr(view, "on_show"):
            view.on_show()

    def update_views(self):
        for view in self.views.values():
            if hasattr(view, "on_state_changed"):
                try:
                    view.on_state_changed()
                except Exception:
                    pass

    def set_status(self, text):
        try:
            self.status_label.configure(text=text)
        except Exception:
            pass

    def log(self, message):
        lv = self.views.get("log")
        if lv and hasattr(lv, "append_line"):
            try:
                lv.append_line(message)
            except Exception:
                pass

    def show_qr_code(self, url):
        if self.qr_window and self.qr_window.winfo_exists():
            try:
                self.qr_window.destroy()
            except Exception:
                pass
        self.qr_window = QRDialog(self.root, self.lang, url)

    def close_qr_window(self):
        if self.qr_window and self.qr_window.winfo_exists():
            try:
                self.qr_window.destroy()
            except Exception:
                pass
            self.qr_window = None

    def show_code_input(self):
        CodeDialog(self.root, self.lang, self._on_code_submitted)

    def _on_code_submitted(self, code):
        if code:
            self.client.submit_code(code)
        else:
            self.client.submit_code("")

    def show_password_input(self):
        PasswordDialog(self.root, self.lang, self._on_password_submitted)

    def _on_password_submitted(self, pwd):
        if pwd:
            self.client.submit_password(pwd)
        else:
            self.client.submit_password("")

    def on_close(self):
        try:
            self.save_settings()
            self.client.disconnect()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass