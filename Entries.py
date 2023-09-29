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
from ModalWindow import *
from Plotter import *


# class for entries storage (класс для хранения текстовых полей)
class Entries:
    def __init__(self):
        self.entries_list = []
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    # adding a new entry and returning the entry widget (добавление нового текстового поля и возврат виджета поля)
    def add_entry(self):
        new_entry = Entry(self.parent_window)
        new_entry.icursor(0)
        new_entry.focus()
        new_entry.pack()
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')
        self.entries_list.append(new_entry)
        return new_entry

    # deleting of active entry (удаление активного текстового поля)
    def delete_entry(self):
        if len(self.entries_list) > 0:
            self.entries_list[-1].destroy()
            self.entries_list.pop()
            plot_button = self.parent_window.get_button_by_name('plot')
            if plot_button:
                plot_button.pack_forget()
            self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')