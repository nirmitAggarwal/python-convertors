import tkinter as tk
from tkinter import TclError


class TkDND:
    def __init__(self, root):
        self._tk = root.tk

        self._tk.call("package", "require", "tkdnd")

    def bindtarget(self, widget, callback, *dndtypes):
        widget.tk.call("tkdnd::bindtarget", widget._w, *dndtypes, callback)
