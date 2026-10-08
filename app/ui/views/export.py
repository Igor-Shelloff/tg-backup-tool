import os
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.ui.views.base import BaseView
from app.ui.theme import theme
from app.ui.components import PageHeader, SectionCard
from app.config import APP_DATA_DIR


class ExportView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.channels_data = {}
        self.export_in_progress = False
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        PageHeader(
            self,
            icon="📤",
            title=self.lang.get("export_title"),
            subtitle=self.lang.get("export_subtitle"),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        ch_card = SectionCard(self.scroll, title=self.lang.get("export_select_channel"))
        ch_card.grid(row=0, column=0, sticky="ew", pady=6, padx=4)
        ch_body = ch_card.body()

        self.channel_combo = ctk.CTkComboBox(
            ch_body, values=[], width=440, state="readonly",
        )
        self.channel_combo.grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
        self.channel_combo.set("")

        ctk.CTkButton(
            ch_body, text=self.lang.get("export_refresh_channels"),
            command=self._refresh_channels, width=180,
        ).grid(row=0, column=1, sticky="w", pady=6)

        opts_card = SectionCard(self.scroll, title=self.lang.get("export_options"))
        opts_card.grid(row=1, column=0, sticky="ew", pady=6, padx=4)
        opts = opts_card.body()

        self.var_name = ctk.BooleanVar(value=True)
        self.var_desc = ctk.BooleanVar(value=True)
        self.var_avatar = ctk.BooleanVar(value=True)
        self.var_messages = ctk.BooleanVar(value=True)
        self.var_media = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(opts, text=self.lang.get("export_name"),
                        variable=self.var_name).grid(row=0, column=0, sticky="w", pady=3)
        ctk.CTkCheckBox(opts, text=self.lang.get("export_description"),
                        variable=self.var_desc).grid(row=1, column=0, sticky="w", pady=3)
        ctk.CTkCheckBox(opts, text=self.lang.get("export_avatar"),
                        variable=self.var_avatar).grid(row=2, column=0, sticky="w", pady=3)
        ctk.CTkCheckBox(opts, text=self.lang.get("export_messages"),
                        variable=self.var_messages).grid(row=3, column=0, sticky="w", pady=3)
        ctk.CTkCheckBox(opts, text=self.lang.get("export_media"),
                        variable=self.var_media).grid(row=4, column=0, sticky="w", pady=3)

        ctk.CTkLabel(opts, text=self.lang.get("export_limit"),
                     anchor="w").grid(row=0, column=1, sticky="w", padx=(30, 6), pady=3)
        self.limit_entry = ctk.CTkEntry(opts, width=100)
        self.limit_entry.insert(0, "0")
        self.limit_entry.grid(row=0, column=2, sticky="w", pady=3)

        path_card = SectionCard(self.scroll, title=self.lang.get("export_path"))
        path_card.grid(row=2, column=0, sticky="ew", pady=6, padx=4)
        pbody = path_card.body()

        self.path_var = ctk.StringVar(value=str(APP_DATA_DIR / "exports"))
        ctk.CTkEntry(pbody, textvariable=self.path_var, width=440).grid(
            row=0, column=0, sticky="ew", padx=(0, 8), pady=6)
        ctk.CTkButton(
            pbody, text=self.lang.get("export_select_folder"),
            command=self._choose_folder, width=180,
        ).grid(row=0, column=1, sticky="w", pady=6)

        action_card = SectionCard(self.scroll)
        action_card.grid(row=3, column=0, sticky="ew", pady=6, padx=4)
        abody = action_card.body()

        self.btn_start = ctk.CTkButton(
            abody, text=self.lang.get("export_start"),
            command=self._start_export, width=220, height=42,
            fg_color=theme.ok, hover_color="#229954",
        )
        self.btn_start.grid(row=0, column=0, sticky="w", pady=6)

        self.btn_stop = ctk.CTkButton(
            abody, text=self.lang.get("export_stop"),
            command=self._stop_export, width=140, height=42,
            fg_color=theme.error, hover_color="#a93226",
            state="disabled",
        )
        self.btn_stop.grid(row=0, column=1, sticky="w", padx=8, pady=6)

        self.progress = ctk.CTkProgressBar(abody, width=560)
        self.progress.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 4))
        self.progress.set(0)

        self.progress_label = ctk.CTkLabel(abody, text="", anchor="w")
        self.progress_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=2)

    def _refresh_channels(self):
        if not self.app.is_authorized:
            messagebox.showerror(
                self.lang.get("error"),
                self.lang.get("export_channel_required"),
                parent=self,
            )
            return
        self.app.log("🔄 " + self.lang.get("export_loading_channels"))
        self.app.client.get_channels(self._on_channels_loaded)

    def _on_channels_loaded(self, result):
        success = isinstance(result, list)
        channels = result if success else []
        if not channels:
            self.channel_combo.configure(values=[])
            self.channel_combo.set("")
            self.app.log("⚠️ " + self.lang.get("export_no_channels"))
            return

        self.channels_data.clear()
        display = []
        for ch in channels:
            name = ch["name"] or "Unnamed"
            if ch.get("username"):
                name += f" (@{ch['username']})"
            self.channels_data[name] = ch
            display.append(name)

        self.channel_combo.configure(values=display)
        self.channel_combo.set(display[0])
        self.app.log(f"✅ {self.lang.get('export_select_channel')}: {len(channels)}")

    def _choose_folder(self):
        folder = filedialog.askdirectory(title=self.lang.get("export_select_folder"))
        if folder:
            self.path_var.set(folder)

    def _start_export(self):
        if self.export_in_progress:
            return
        if not self.app.is_authorized:
            messagebox.showerror(
                self.lang.get("error"),
                self.lang.get("export_channel_required"),
                parent=self,
            )
            return

        selection = self.channel_combo.get()
        if not selection or selection not in self.channels_data:
            messagebox.showerror(
                self.lang.get("error"),
                self.lang.get("export_select_channel_first"),
                parent=self,
            )
            return

        base_path = self.path_var.get().strip()
        if not base_path:
            messagebox.showerror(
                self.lang.get("error"),
                self.lang.get("export_select_folder_first"),
                parent=self,
            )
            return

        ch = self.channels_data[selection]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = "".join(c for c in (ch["name"] or "channel") if c.isalnum() or c in " _-").strip()
        safe = safe or "channel"
        export_path = Path(base_path) / f"backup_{safe}_{ts}"

        try:
            limit = int(self.limit_entry.get() or "0")
        except ValueError:
            limit = 0

        options = {
            "export_name": self.var_name.get(),
            "export_description": self.var_desc.get(),
            "export_avatar": self.var_avatar.get(),
            "export_messages": self.var_messages.get(),
            "export_media": self.var_media.get(),
            "limit_messages": limit,
        }

        self.export_in_progress = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.progress.set(0)
        self.progress_label.configure(text=self.lang.get("export_in_progress"))
        self.app.log("📤 " + self.lang.get("export_in_progress"))

        self.app.client.export_channel(
            ch["id"], str(export_path), options,
            self._on_progress, self._on_export_done,
        )

    def _on_progress(self, count):
        self.progress_label.configure(
            text=f"{self.lang.get('export_in_progress')} {count}",
        )

    def _on_export_done(self, result):
        self.export_in_progress = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.progress.set(1 if result.get("success") else 0)

        if result.get("success"):
            count = result.get("messages", 0)
            path = result.get("path", "")
            self.progress_label.configure(
                text=f"{self.lang.get('export_done')}: {count}",
            )
            self.app.log(f"✅ {self.lang.get('export_done')}: {path} ({count})")
            messagebox.showinfo(
                self.lang.get("status_ok"),
                f"{self.lang.get('export_done')}\n\n{path}\n\n{count}",
                parent=self,
            )
        else:
            err = result.get("error", "unknown")
            self.progress_label.configure(text=self.lang.get("export_failed"))
            self.app.log(f"❌ {self.lang.get('export_failed')}: {err}")
            messagebox.showerror(
                self.lang.get("error"),
                f"{self.lang.get('export_failed')}: {err}",
                parent=self,
            )

    def _stop_export(self):
        self.app.client.stop_export()
        self.app.log("⏹ " + self.lang.get("export_stop"))

    def on_show(self):
        if self.app.is_authorized and not self.channels_data:
            self._refresh_channels()

    def on_state_changed(self):
        pass