import json
import customtkinter as ctk
from tkinter import messagebox

from app.ui.views.base import BaseView
from app.ui.theme import theme
from app.ui.components import PageHeader, SectionCard
from app.config import SETTINGS_FILE


class AuthView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        PageHeader(
            self,
            icon="🔐",
            title=self.lang.get("auth_title"),
            subtitle=self.lang.get("auth_subtitle"),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        creds = SectionCard(self.scroll, title="API")
        creds.grid(row=0, column=0, sticky="ew", pady=6, padx=4)
        body = creds.body()

        ctk.CTkLabel(body, text=self.lang.get("auth_api_id"), anchor="w").grid(
            row=0, column=0, sticky="w", pady=6)
        self.api_id_entry = ctk.CTkEntry(body, width=320)
        self.api_id_entry.grid(row=0, column=1, sticky="w", padx=8, pady=6)

        ctk.CTkLabel(body, text=self.lang.get("auth_api_hash"), anchor="w").grid(
            row=1, column=0, sticky="w", pady=6)
        self.api_hash_entry = ctk.CTkEntry(body, width=320)
        self.api_hash_entry.grid(row=1, column=1, sticky="w", padx=8, pady=6)

        ctk.CTkLabel(body, text=self.lang.get("auth_phone"), anchor="w").grid(
            row=2, column=0, sticky="w", pady=6)
        self.phone_entry = ctk.CTkEntry(body, width=320, placeholder_text="+7...")
        self.phone_entry.grid(row=2, column=1, sticky="w", padx=8, pady=6)

        ctk.CTkLabel(body, text=self.lang.get("auth_session"), anchor="w").grid(
            row=3, column=0, sticky="w", pady=6)
        self.session_entry = ctk.CTkEntry(body, width=320)
        self.session_entry.insert(0, "backup_session")
        self.session_entry.grid(row=3, column=1, sticky="w", padx=8, pady=6)

        ctk.CTkLabel(
            body, text=self.lang.get("auth_hint"),
            text_color=theme.fg_muted, font=ctk.CTkFont(size=10),
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))

        actions = SectionCard(self.scroll)
        actions.grid(row=1, column=0, sticky="ew", pady=6, padx=4)
        abody = actions.body()

        btn_row = ctk.CTkFrame(abody, fg_color="transparent")
        btn_row.grid(row=0, column=0, sticky="w")

        self.btn_phone = ctk.CTkButton(
            btn_row, text=self.lang.get("auth_btn_phone"),
            command=self._authorize_phone, width=200, height=42,
        )
        self.btn_phone.pack(side="left", padx=(0, 8))

        self.btn_qr = ctk.CTkButton(
            btn_row, text=self.lang.get("auth_btn_qr"),
            command=self._authorize_qr, width=200, height=42,
            fg_color=theme.accent, hover_color="#1f5580",
        )
        self.btn_qr.pack(side="left", padx=8)

        self.btn_logout = ctk.CTkButton(
            btn_row, text=self.lang.get("auth_btn_logout"),
            command=self._logout, width=140, height=42,
            fg_color="transparent", border_width=1,
            border_color=theme.error, text_color=theme.error,
            hover_color="#4a1a1a",
        )
        self.btn_logout.pack(side="left", padx=8)

        status_card = SectionCard(self.scroll, title=self.lang.get("auth_title"))
        status_card.grid(row=2, column=0, sticky="ew", pady=6, padx=4)
        sbody = status_card.body()

        self.status_label = ctk.CTkLabel(
            sbody, text=self.lang.get("auth_status_not_authorized"),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=theme.error, anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="w", pady=4)

        self.account_label = ctk.CTkLabel(sbody, text="", anchor="w")
        self.account_label.grid(row=1, column=0, sticky="w", pady=4)

        self._load_settings()
        self._update_buttons()

    def _load_settings(self):
        try:
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.api_id_entry.insert(0, str(data.get("api_id", "")))
                self.api_hash_entry.insert(0, str(data.get("api_hash", "")))
                self.phone_entry.insert(0, str(data.get("phone", "")))
                session = data.get("session_name", "backup_session")
                self.session_entry.delete(0, "end")
                self.session_entry.insert(0, session)
        except Exception:
            pass

    def _save_settings(self):
        try:
            data = {}
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            data["api_id"] = self.api_id_entry.get().strip()
            data["api_hash"] = self.api_hash_entry.get().strip()
            data["phone"] = self.phone_entry.get().strip()
            data["session_name"] = self.session_entry.get().strip() or "backup_session"
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _get_credentials(self):
        api_id = self.api_id_entry.get().strip()
        api_hash = self.api_hash_entry.get().strip()
        phone = self.phone_entry.get().strip()
        session = self.session_entry.get().strip() or "backup_session"
        return api_id, api_hash, phone, session

    def _validate(self, need_phone=True):
        api_id, api_hash, phone, session = self._get_credentials()
        if not api_id or not api_hash or (need_phone and not phone):
            messagebox.showerror(
                self.lang.get("error"),
                self.lang.get("auth_fill_fields"),
                parent=self,
            )
            return None
        try:
            int(api_id)
        except ValueError:
            messagebox.showerror(
                self.lang.get("error"),
                self.lang.get("auth_api_must_be_number"),
                parent=self,
            )
            return None
        return api_id, api_hash, phone, session

    def _authorize_phone(self):
        creds = self._validate(need_phone=True)
        if not creds:
            return
        api_id, api_hash, phone, session = creds
        if self.app.auth_in_progress:
            messagebox.showinfo(
                self.lang.get("info"),
                self.lang.get("auth_already_running"),
                parent=self,
            )
            return
        self._save_settings()
        self.app.auth_in_progress = True
        self._update_buttons()
        self.app.log("🔐 " + self.lang.get("auth_btn_phone"))
        self.app.client.authorize_phone(
            int(api_id), api_hash, phone, session, self._on_auth_result,
        )

    def _authorize_qr(self):
        creds = self._validate(need_phone=False)
        if not creds:
            return
        api_id, api_hash, phone, session = creds
        if self.app.auth_in_progress:
            messagebox.showinfo(
                self.lang.get("info"),
                self.lang.get("auth_already_running"),
                parent=self,
            )
            return
        self._save_settings()
        self.app.auth_in_progress = True
        self._update_buttons()
        self.app.log("🔐 " + self.lang.get("auth_btn_qr"))
        self.app.client.authorize_qr(
            int(api_id), api_hash, session, self._on_auth_result,
        )

    def _on_auth_result(self, result):
        self.app.auth_in_progress = False
        success, info = result if isinstance(result, tuple) else (False, str(result))
        if success:
            self.app.user_info = info
            self.app.is_authorized = True
            self.app.close_qr_window()
            self.app.log("✅ " + self.lang.get("auth_success") + f": {info}")
            self.app.set_status(self.lang.get("auth_status_authorized"))
        else:
            self.app.is_authorized = False
            self.app.close_qr_window()
            self.app.log("❌ " + self.lang.get("auth_failed") + f": {info}")
            self.app.set_status(self.lang.get("auth_failed"))
        self._update_buttons()
        self.app.update_views()

    def _logout(self):
        if not self.app.is_authorized:
            return
        if not messagebox.askyesno(
            self.lang.get("confirm"),
            self.lang.get("auth_confirm_logout"),
            parent=self,
        ):
            return
        self.app.client.logout(self._on_logout)
        self.app.is_authorized = False
        self.app.user_info = ""
        self.app.log("🚪 " + self.lang.get("auth_logged_out"))

    def _on_logout(self, result=None):
        self._update_buttons()
        self.app.update_views()

    def _update_buttons(self):
        if self.app.auth_in_progress:
            self.btn_phone.configure(state="disabled")
            self.btn_qr.configure(state="disabled")
        else:
            self.btn_phone.configure(state="normal")
            self.btn_qr.configure(state="normal")

        if self.app.is_authorized:
            self.status_label.configure(
                text=self.lang.get("auth_status_authorized"),
                text_color=theme.ok,
            )
            self.account_label.configure(text=self.app.user_info)
            self.btn_logout.configure(state="normal")
        else:
            self.status_label.configure(
                text=self.lang.get("auth_status_not_authorized"),
                text_color=theme.error,
            )
            self.account_label.configure(text="")
            self.btn_logout.configure(state="disabled")

    def on_show(self):
        self._update_buttons()

    def on_state_changed(self):
        self._update_buttons()