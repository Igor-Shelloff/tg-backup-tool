import tkinter as tk
import customtkinter as ctk


def _resolve_target(widget):
    if isinstance(widget, ctk.CTkEntry):
        return widget._entry, False
    if isinstance(widget, ctk.CTkTextbox):
        return widget._textbox, True
    if isinstance(widget, ctk.CTkComboBox):
        return widget._entry, False
    if isinstance(widget, tk.Text):
        return widget, True
    if isinstance(widget, tk.Entry):
        return widget, False
    return None, False


def attach_context_menu(widget, lang=None):
    target, is_text = _resolve_target(widget)
    if target is None:
        return

    def labels():
        ru = lang is not None and lang.current_lang == "ru"
        return {
            "cut": "Вырезать" if ru else "Cut",
            "copy": "Копировать" if ru else "Copy",
            "paste": "Вставить" if ru else "Paste",
            "select_all": "Выделить всё" if ru else "Select All",
        }

    def do_cut():
        try:
            target.event_generate("<<Cut>>")
        except Exception:
            pass

    def do_copy():
        try:
            target.event_generate("<<Copy>>")
        except Exception:
            pass

    def do_paste():
        try:
            target.event_generate("<<Paste>>")
        except Exception:
            pass

    def do_select_all():
        try:
            if is_text:
                target.tag_add("sel", "1.0", "end-1c")
                target.mark_set("insert", "1.0")
                target.see("insert")
            else:
                target.select_range(0, "end")
                target.icursor("end")
        except Exception:
            pass

    def show(event):
        l = labels()
        m = tk.Menu(target, tearoff=0)
        m.add_command(label=l["cut"], command=do_cut)
        m.add_command(label=l["copy"], command=do_copy)
        m.add_command(label=l["paste"], command=do_paste)
        m.add_separator()
        m.add_command(label=l["select_all"], command=do_select_all)
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    target.bind("<Button-3>", show, add="+")

    for seq, fn in (
        ("<Control-c>", do_copy),
        ("<Control-C>", do_copy),
        ("<Control-v>", do_paste),
        ("<Control-V>", do_paste),
        ("<Control-x>", do_cut),
        ("<Control-X>", do_cut),
        ("<Control-a>", do_select_all),
        ("<Control-A>", do_select_all),
    ):
        target.bind(seq, lambda e, f=fn: (f(), "break")[1], add="+")


def attach_context_menu_recursive(widget, lang=None):
    if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox, ctk.CTkComboBox)):
        attach_context_menu(widget, lang)
    try:
        children = widget.winfo_children()
    except Exception:
        children = []
    for child in children:
        attach_context_menu_recursive(child, lang)