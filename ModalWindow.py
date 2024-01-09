import json
import matplotlib

import numexpr as ne
import numpy as np

from functools import partial
from tkinter import *
from tkinter.filedialog import asksaveasfile

from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

from App import *
from Buttons import *
from Commands import *
from Entries import *
from Plotter import *

# class for generate modal windows (класс для генерации модальных окон)
class ModalWindow:
    def __init__(self, parent, title, labeltext=''):
        self.buttons = []
        self.top = Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        if len(title) > 0:
            self.top.title(title)
        if len(labeltext) == 0:
            labeltext = 'ModalWindow with no text'
        Label(self.top, text=labeltext).pack()

    def add_button(self, button):
        self.buttons.append(button)
        button.pack(pady=5)

    def cancel(self):
        self.top.destroy()
