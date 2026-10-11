import os
import sys
from tkinter import messagebox

import tavern_shared.theme as _theme

MODS_BUTTON = "\U0001F9EA Mods"
ADDONS_BUTTON = "\U0001F9E9 Addons"
SAVE_BUTTON = "\U0001F4BE Save (restart required to apply)"
MODS_FOLDER_TEXT = "\U0001F4C1 Mods Folder"
ADDONS_FOLDER_TEXT = "\U0001F4C1 Addons Folder"
OPEN_ADDONS_FOLDER_TEXT = "\U0001F4C1 Open Addons Folder"


def _open(path, parent):
    try:
        os.startfile(path)
    except OSError as e:
        messagebox.showerror("Open Folders", f"Could not open {path}\n\n{e}", parent=parent)


def _open_mods(root):
    try:
        exe = root.v_exe.get().strip()
    except Exception:
        exe = ""
    if not exe or not os.path.isfile(exe):
        messagebox.showerror("Game not found",
            "Please set the path to 'A Township Tale.exe' above first.", parent=root)
        return
    mods = os.path.join(os.path.dirname(exe), "Mods")
    if not os.path.isdir(mods):
        messagebox.showinfo("No Mods folder",
            "There is no Mods folder next to the game yet. Install MelonLoader with the "
            "Mods button, then start the game once.", parent=root)
        return
    _open(mods, root)


def _addons_dir(widget):
    window = widget.winfo_toplevel()
    loader = getattr(window, "_addon_loader", None)
    if loader is None:
        side = type(window).__module__.split(".")[0]
        loader = sys.modules.get(side + ".core.addon_loader")
    try:
        return loader.addons_dir()
    except Exception:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _open_addons(widget):
    _open(_addons_dir(widget), widget.winfo_toplevel())


def _has(parent, text):
    for child in parent.winfo_children():
        try:
            if child.cget("text") == text:
                return True
        except Exception:
            pass
    return False


def _add_mods_folder(anchor):
    try:
        root = anchor.winfo_toplevel()
        if not hasattr(root, "v_exe") or _has(anchor.master, MODS_FOLDER_TEXT):
            return
        button = _theme._btn(anchor.master, MODS_FOLDER_TEXT, lambda: _open_mods(root),
                             font=("Segoe UI", 9), pady=5, padx=10)
        button.pack(side="left", padx=(6, 0), after=anchor)
    except Exception:
        pass


def _add_addons_folder(anchor):
    try:
        root = anchor.winfo_toplevel()
        if not hasattr(root, "_open_addons") or _has(anchor.master, ADDONS_FOLDER_TEXT):
            return
        button = _theme._btn(anchor.master, ADDONS_FOLDER_TEXT, lambda: _open_addons(anchor),
                             font=("Segoe UI", 7), pady=2, padx=6)
        button.pack(side="right", padx=(0, 6), after=anchor)
    except Exception:
        pass


def _add_open_addons_folder(save):
    try:
        window = save.winfo_toplevel()
        if _has(window, OPEN_ADDONS_FOLDER_TEXT):
            return
        button = _theme._btn(window, OPEN_ADDONS_FOLDER_TEXT, lambda: _open_addons(window),
                             font=("Segoe UI", 9), pady=6)
        button.pack(fill="x", padx=16, pady=(0, 16), after=save)
        save.pack_configure(pady=(0, 6))
    except Exception:
        pass


def _wrap(orig):
    def _btn(parent, text, cmd, style="normal", **kw):
        button = orig(parent, text, cmd, style, **kw)
        if text == MODS_BUTTON:
            button.after_idle(lambda: _add_mods_folder(button))
        elif text == ADDONS_BUTTON:
            button.after_idle(lambda: _add_addons_folder(button))
        elif text == SAVE_BUTTON and type(parent).__name__ == "AddonManagerWindow":
            button.after_idle(lambda: _add_open_addons_folder(button))
        return button
    return _btn


_theme._btn = _wrap(_theme._btn)

for _name in ("client.core.launcher_window", "server.core.launcher_window",
              "tavern_shared.addon_manager_window"):
    _module = sys.modules.get(_name)
    if _module is not None and callable(getattr(_module, "_btn", None)):
        _module._btn = _wrap(_module._btn)
