from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.ui.views.base import BaseView
from app.ui.theme import theme
from app.ui.components import PageHeader, SectionCard


class ImportView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.import_in_progress = False
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        PageHeader(
            self,
            icon="📥",
            title=self.lang.get("import_title"),
            subtitle=self.lang.get("import_subtitle"),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        path_card = SectionCard(self.scroll, title=self.lang.get("import_select_backup"))
        path_card.grid(row=0, column=0, sticky="ew", pady=6, padx=4)
        pbody = path_card.body()

        self.path_var = ctk.StringVar()
        ctk.CTkEntry(pbody, textvariable=self.path_var, width=440).grid(
            row=0, column=0, sticky="ew", padx=(0, 8), pady=6)
        ctk.CTkButton(
            pbody, text=self.lang.get("import_select_folder"),
            command=self._choose_folder, width=180,
        ).grid(row=0, column=1, sticky="w", pady=6)

        opts_card = SectionCard(self.scroll, title=self.lang.get("import_options"))
        opts_card.grid(row=1, column=0, sticky="ew", pady=6, padx=4)
        opts = opts_card.body()

        self.var_name = ctk.BooleanVar(value=True)
        self.var_desc = ctk.BooleanVar(value=True)
        self.var_avatar = ctk.BooleanVar(value=True)
        self.var_messages = ctk.BooleanVar(value=True)
        self.var_media = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(opts, text=self.lang.get("import_name"),
                        variable=self.var_name).grid(row=0, column=0, sticky="w", pady=3)
        ctk.CTkCheckBox(opts, text=self.lang.get("import_description"),
                        variable=self.var_desc).grid(row=1, column=0, sticky="w", pady=3)
        ctk.CTkCheckBox(opts, text=self.lang.get("import_avatar"),
                        variable=self.var_avatar).grid(row=2, column=0, sticky="w", pady=3)
        ctk.CTkCheckBox(opts, text=self.lang.get("import_messages"),
                        variable=self.var_messages).grid(row=3, column=0, sticky="w", pady=3)
        ctk.CTkCheckBox(opts, text=self.lang.get("import_media"),
                        variable=self.var_media).grid(row=4, column=0, sticky="w", pady=3)

        ctk.CTkLabel(opts, text=self.lang.get("import_new_name"),
                     anchor="w").grid(row=0, column=1, sticky="w", padx=(30, 6), pady=3)
        self.name_entry = ctk.CTkEntry(opts, width=220)
        self.name_entry.insert(0, self.lang.get("import_new_channel_default"))
        self.name_entry.grid(row=0, column=2, sticky="w", pady=3)

        ctk.CTkLabel(opts, text=self.lang.get("import_delay"),
                     anchor="w").grid(row=1, column=1, sticky="w", padx=(30, 6), pady=3)
        self.delay_entry = ctk.CTkEntry(opts, width=100)
        self.delay_entry.insert(0, "1.0")
        self.delay_entry.grid(row=1, column=2, sticky="w", pady=3)

        action_card = SectionCard(self.scroll)
        action_card.grid(row=2, column=0, sticky="ew", pady=6, padx=4)
        abody = action_card.body()

        self.btn_start = ctk.CTkButton(
            abody, text=self.lang.get("import_start"),
            command=self._start_import, width=220, height=42,
            fg_color=theme.ok, hover_color="#229954",
        )
        self.btn_start.grid(row=0, column=0, sticky="w", pady=6)

        self.btn_stop = ctk.CTkButton(
            abody, text=self.lang.get("import_stop"),
            command=self._stop_import, width=140, height=42,
            fg_color=theme.error, hover_color="#a93226",
            state="disabled",
        )
        self.btn_stop.grid(row=0, column=1, sticky="w", padx=8, pady=6)

        self.progress = ctk.CTkProgressBar(abody, width=560)
        self.progress.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 4))
        self.progress.set(0)

        self.progress_label = ctk.CTkLabel(abody, text="", anchor="w")
        self.progress_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=2)

    def _choose_folder(self):
        folder = filedialog.askdirectory(title=self.lang.get("import_select_folder"))
        if folder:
            self.path_var.set(folder)

    def _start_import(self):
        if self.import_in_progress:
            return
        if not self.app.is_authorized:
            messagebox.showerror(
                self.lang.get("error"),
                self.lang.get("export_channel_required"),
                parent=self,
            )
            return

        path = self.path_var.get().strip()
        if not path:
            messagebox.showerror(
                self.lang.get("error"),
                self.lang.get("import_select_folder_first"),
                parent=self,
            )
            return

        if not (Path(path) / "channel_data.json").exists():
            messagebox.showerror(
                self.lang.get("error"),
                self.lang.get("import_no_backup"),
                parent=self,
            )
            return

        try:
            delay = float(self.delay_entry.get() or "1.0")
        except ValueError:
            delay = 1.0

        options = {
            "import_name": self.var_name.get(),
            "import_description": self.var_desc.get(),
            "import_avatar": self.var_avatar.get(),
            "import_messages": self.var_messages.get(),
            "import_media": self.var_media.get(),
            "new_channel_name": self.name_entry.get().strip()
                or self.lang.get("import_new_channel_default"),
            "delay": delay,
        }

        self.import_in_progress = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.progress.set(0)
        self.progress_label.configure(text=self.lang.get("import_in_progress"))
        self.app.log("📥 " + self.lang.get("import_in_progress"))

        self.app.client.import_channel(
            path, options, self._on_progress, self._on_import_done,
        )

    def _on_progress(self, current, total):
        if total > 0:
            self.progress.set(current / total)
        self.progress_label.configure(
            text=f"{self.lang.get('import_in_progress')} {current}/{total}",
        )

    def _on_import_done(self, result):
        self.import_in_progress = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")

        if result.get("success"):
            self.progress.set(1)
            count = result.get("imported", 0)
            self.progress_label.configure(
                text=f"{self.lang.get('import_done')}: {count}",
            )
            self.app.log(f"✅ {self.lang.get('import_done')}: {count}")
            messagebox.showinfo(
                self.lang.get("status_ok"),
                f"{self.lang.get('import_done')}\n\n{count}",
                parent=self,
            )
        else:
            err = result.get("error", "unknown")
            self.progress_label.configure(text=self.lang.get("import_failed"))
            self.app.log(f"❌ {self.lang.get('import_failed')}: {err}")
            messagebox.showerror(
                self.lang.get("error"),
                f"{self.lang.get('import_failed')}: {err}",
                parent=self,
            )

    def _stop_import(self):
        self.app.client.stop_import()
        self.app.log("⏹ " + self.lang.get("import_stop"))

    def on_show(self):
        pass

    def on_state_changed(self):
        pass