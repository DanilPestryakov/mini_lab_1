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

    # Подтверждение удаления после открытия модального окна подтверждения
    def confirm_delete(self, entry, modal):
        entry.destroy()
        self.entries_list.remove(entry)
        modal.top.destroy()
        # Обновляем график после удаления записи
        self.parent_window.commands.plot()

    # удаляем активное поле и обновляем график после его удаления
    def delete_entry(self):
        if len(self.entries_list) > 0:
            # Выбор активного поля
            focused_entry = self.parent_window.focus_get()

            if focused_entry in self.entries_list:
                if focused_entry.get().strip():
                    modal = ModalWindow(self.parent_window, title='Подтверждение', labeltext='Удалить выбранное поле вместе с графиком функции?')
                    ok_button = Button(master=modal.top, text='Да', command=lambda: self.confirm_delete(focused_entry, modal))
                    cancel_button = Button(master=modal.top, text='Отмена', command=modal.cancel)
                    modal.add_button(ok_button)
                    modal.add_button(cancel_button)
                else:
                    # Если поле пустое удаляем без вопросов
                    focused_entry.destroy()
                    self.entries_list.remove(focused_entry)