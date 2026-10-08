import customtkinter as ctk


class BaseView(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.app = app
        self.lang = app.lang

    def on_show(self):
        pass

    def on_hide(self):
        pass

    def on_state_changed(self):
        pass