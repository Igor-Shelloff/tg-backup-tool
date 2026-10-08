import io
import threading
import time

import customtkinter as ctk
import qrcode
from PIL import Image


class QRDialog(ctk.CTkToplevel):
    def __init__(self, parent, lang, url, refresh_callback=None):
        super().__init__(parent)
        self.lang = lang
        self.url = url
        self.refresh_callback = refresh_callback
        self._closed = False

        self.title(lang.get("qr_title"))
        self.geometry("420x560")
        self.resizable(False, False)
        self.transient(parent)
        try:
            self.grab_set()
        except Exception:
            pass

        ctk.CTkLabel(
            self, text=lang.get("qr_title"),
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 8))

        ctk.CTkLabel(
            self, text=lang.get("qr_hint"),
            wraplength=360, justify="center",
            font=ctk.CTkFont(size=11),
        ).pack(pady=(0, 12))

        self.qr_label = ctk.CTkLabel(self, text="")
        self.qr_label.pack(pady=10)

        self.status = ctk.CTkLabel(
            self, text=lang.get("qr_waiting"),
            font=ctk.CTkFont(size=12),
        )
        self.status.pack(pady=8)

        if refresh_callback:
            ctk.CTkButton(
                self, text=lang.get("qr_refresh"),
                command=self._refresh, width=180,
            ).pack(pady=(6, 20))

        self._render_qr(self.url)

    def _render_qr(self, url):
        img = qrcode.make(url)
        img = img.resize((300, 300), Image.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 300))
        self.qr_label.configure(image=ctk_img)
        self.qr_label.image = ctk_img

    def _refresh(self):
        if self.refresh_callback:
            self.refresh_callback()

    def update_url(self, url):
        if self._closed:
            return
        self._render_qr(url)

    def set_status(self, text, color=None):
        if self._closed:
            return
        self.status.configure(text=text)
        if color:
            self.status.configure(text_color=color)

    def destroy(self):
        self._closed = True
        try:
            super().destroy()
        except Exception:
            pass