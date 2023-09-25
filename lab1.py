import json
import matplotlib

import numexpr as ne
import numpy as np
import tkinter as tk

from functools import partial
from tkinter import *
from tkinter.filedialog import asksaveasfile

from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from pynput import keyboard

import os
import subprocess
FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

import easygui

matplotlib.use('TkAgg')


# class for entries storage (класс для хранения текстовых полей)
class Entries:
    def __init__(self):
        self.entries_list = []
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    # adding of new entry (добавление нового текстового поля)
    def add_entry(self):
        current_entry = None

        def on_focus(evt):
            global current_entry
            current_entry = evt.widget
        new_entry = Entry(self.parent_window)
        new_entry.icursor(0)
        new_entry.focus()
        new_entry.bind('<FocusIn>', on_focus)
        new_entry.pack()
        plot_button = self.parent_window.get_button_by_name('plot')
        plot_button_2 = self.parent_window.get_button_by_name('clear')
        if plot_button:
            plot_button.pack_forget()
        if plot_button_2:
            plot_button_2.pack_forget()
        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')
        self.parent_window.add_button('clear', 'Clear', 'clear', hot_key='<Control-c>')
        self.entries_list.append(new_entry)

    def cleaning(self):
        plot_button = self.parent_window.get_button_by_name('plot')
        clear_button = self.parent_window.get_button_by_name('clear')
        if plot_button:
            plot_button.pack_forget()
        if clear_button:
            clear_button.pack_forget()
        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')
        self.parent_window.add_button('clear', 'Clear', 'clear', hot_key='<Control-c>')


# class for plotting (класс для построения графиков)
class Plotter:
    def __init__(self, x_min=-20, x_max=20, dx=0.01):
        self.x_min = x_min
        self.x_max = x_max
        self.dx = dx
        self._last_plotted_list_of_function = None
        self._last_plotted_figure = None
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    # plotting of graphics (построение графиков функций)
    def plot(self, list_of_function, title='Графики функций', x_label='x', y_label='y', need_legend=True):
        fig = plt.figure()

        x = np.arange(self.x_min, self.x_max, self.dx)

        new_funcs = [f if 'x' in f else 'x/x * ({})'.format(f) for f in list_of_function]

        ax = fig.add_subplot(1, 1, 1)
        for func in new_funcs:
            ax.plot(x, ne.evaluate(func), linewidth=1.5)

        fig.suptitle(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if need_legend:
            plt.legend(list_of_function)
        self._last_plotted_list_of_function = list_of_function
        self._last_plotted_figure = fig
        return fig


# class for commands storage (класс для хранения команд)
class Commands:
    class State:
        def __init__(self):
            self.list_of_function = []

        def save_state(self):
            tmp_dict = {'list_of_function': self.list_of_function}
            file_out = asksaveasfile(defaultextension=".json")
            if file_out is not None:
                json.dump(tmp_dict, file_out)
            return self

        def reset_state(self):
            self.list_of_function = []

    def __init__(self):
        self.command_dict = {}
        self.__figure_canvas = None
        self.__navigation_toolbar = None
        self._state = Commands.State()
        self.__empty_entry_counter = 0
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    def add_command(self, name, command):
        self.command_dict[name] = command

    def get_command_by_name(self, command_name):
        return self.command_dict[command_name]

    def __forget_canvas(self):
        if self.__figure_canvas is not None:
            self.__figure_canvas.get_tk_widget().pack_forget()

    def __forget_navigation(self):
        if self.__navigation_toolbar is not None:
            self.__navigation_toolbar.pack_forget()

    def plot(self, *args, **kwargs):
        def is_not_blank(s):
            return bool(s and not s.isspace())

        self._state.reset_state()
        list_of_function = []
        for entry in self.parent_window.entries.entries_list:
            get_func_str = entry.get()
            self._state.list_of_function.append(get_func_str)
            if is_not_blank(get_func_str):
                list_of_function.append(get_func_str)
            else:
                if self.__empty_entry_counter == 0:
                    mw = ModalWindow(self.parent_window, title='Пустая строка', labeltext='Это пример модального окна, '
                                                                                          'возникающий, если ты ввел '
                                                                                          'пустую '
                                                                                          'строку. С этим ничего '
                                                                                          'делать не нужно. '
                                                                                          'Просто нажми OK :)')
                    ok_button = Button(master=mw.top, text='OK', command=mw.cancel)
                    mw.add_button(ok_button)
                    self.__empty_entry_counter = 1
        self.__empty_entry_counter = 0
        figure = self.parent_window.plotter.plot(list_of_function)
        self._state.figure = figure
        self.__forget_canvas()
        self.__figure_canvas = FigureCanvasTkAgg(figure, self.parent_window)
        self.__forget_navigation()
        self.__navigation_toolbar = NavigationToolbar2Tk(self.__figure_canvas, self.parent_window)
        self.__figure_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
        clear_button = self.parent_window.get_button_by_name('clear')
        if clear_button:
            clear_button.pack_forget()

    def clear(self, *args, **kwargs):
        def is_not_blank(s):
            return bool(s and not s.isspace())
        if current_entry is not None:
            get_func_str = current_entry.get()
        else:
            get_func_str = self.parent_window.entries.entries_list[-1].get()
        # get_func_str = self.parent_window.entries.entries_list[-1].get()
        if is_not_blank(get_func_str):
            mw = ModalWindow(self.parent_window, title='Внимание', labeltext='Выбранная функция удалена')
            ok_button = Button(master=mw.top, text='OK', command=mw.cancel)
            mw.add_button(ok_button)
        # self.parent_window.entries.entries_list[-1].delete(0, END)
        current_entry.delete(0, END)
        for i in range (len(self.parent_window.entries.entries_list)-1, -1, -1):
            if len(self.parent_window.entries.entries_list) != 1:
                func = self.parent_window.entries.entries_list[i].get()
                if func == "":
                    self.parent_window.entries.entries_list[i].destroy()
                    self.parent_window.entries.entries_list.pop(i)

    def clear_active_plot(self, *args, **kwargs):
        def is_not_blank(s):
            return bool(s and not s.isspace())
        if current_entry is not None:
            get_func_str = current_entry.get()
        else:
            get_func_str = self.parent_window.entries.entries_list[-1].get()
        # get_func_str = self.parent_window.entries.entries_list[-1].get()
        if is_not_blank(get_func_str):
            mw = ModalWindow(self.parent_window, title='Внимание', labeltext='Выбранная функция удалена вместе с графиком')
            ok_button = Button(master=mw.top, text='OK', command=mw.cancel)
            mw.add_button(ok_button)
        # self.parent_window.entries.entries_list[-1].delete(0, END)
        current_entry.delete(0, END)
        if len(self.parent_window.entries.entries_list) != 1:
            for i in range (len(self.parent_window.entries.entries_list)-1, -1, -1):
                func = self.parent_window.entries.entries_list[i].get()
                if func == "":
                    self.parent_window.entries.entries_list[i].destroy()
                    self.parent_window.entries.entries_list.pop(i)
            self.plot()
        else:
            self.clear_all()

    def clear_all(self, *args, **kwargs):
        def is_not_blank(s):
            return bool(s and not s.isspace())
        f=0
        for entry in self.parent_window.entries.entries_list:
            get_func_str = entry.get()
            if is_not_blank(get_func_str):
                f=1
        if f:
            mw = ModalWindow(self.parent_window, title='Внимание', labeltext='Все данные удалены')
            ok_button = Button(master=mw.top, text='OK', command=mw.cancel)
            mw.add_button(ok_button)
        self.parent_window.entries.entries_list[0].delete(0, END)
        for i in range(len(self.parent_window.entries.entries_list)-1, 0, -1):
            self.parent_window.entries.entries_list[i].destroy()
            self.parent_window.entries.entries_list.pop(i)
        # self.parent_window.entries.entries_list = [self.parent_window.entries.entries_list[0]]
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.cleaning()

    def add_func(self, *args, **kwargs):
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.add_entry()

    def save_as(self):
        self._state.save_state()
        return self

    def open_file(self):
        input_file = easygui.fileopenbox(filetypes=["*.json"])
        file = open(input_file)
        str_json = file.read()
        print(str_json)
        str = json.loads(str_json)
        print(str)
        list_of_func = str['list_of_function']
        self.clear_all()
        self.parent_window.entries.entries_list[0].insert(0, list_of_func[0])
        for i in range(1, len(list_of_func)):
            self.parent_window.entries.add_entry()
            self.parent_window.entries.entries_list[i].insert(0, list_of_func[i])
        self.plot()

    def create_template(self, *args, **kwargs):
        def is_not_blank(s):
            return bool(s and not s.isspace())
        if current_entry is not None:
            get_func_str = current_entry.get()
        else:
            get_func_str = self.parent_window.entries.entries_list[-1].get()
        # get_func_str = self.parent_window.entries.entries_list[-1].get()
        if is_not_blank(get_func_str):
            mw = ModalWindow(self.parent_window, title='Внимание', labeltext='Создание шаблона')
            ok_button = Button(master=mw.top, text='OK', command=mw.cancel)
            mw.add_button(ok_button)
            app.add_template(get_func_str)

    # def home_page(self, *args, **kwargs):
    #     self.clear_all()

    def draw_func(self, func):
        self.clear_all()
        self.parent_window.entries.entries_list[0].insert(0,func)
        self._state.reset_state()
        list_of_function = []
        self._state.list_of_function.append(func)
        list_of_function.append(func)
        figure = self.parent_window.plotter.plot(list_of_function)
        self._state.figure = figure
        self.__forget_canvas()
        self.__figure_canvas = FigureCanvasTkAgg(figure, self.parent_window)
        self.__forget_navigation()
        self.__navigation_toolbar = NavigationToolbar2Tk(self.__figure_canvas, self.parent_window)
        self.__figure_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
        clear_button = self.parent_window.get_button_by_name('clear')
        if clear_button:
            clear_button.pack_forget()


# class for buttons storage (класс для хранения кнопок)
class Buttons:
    def __init__(self):
        self.buttons = {}
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    def add_button(self, name, text, command):
        new_button = Button(master=self.parent_window, text=text, command=command)
        self.buttons[name] = new_button
        return new_button

    def delete_button(self, name):
        button = self.buttons.get(name)
        if button:
            button.pack_forget()


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
            labeltext = 'Default text'
        Label(self.top, text=labeltext).pack()

    def add_button(self, button):
        self.buttons.append(button)
        button.pack(pady=5)

    def cancel(self):
        self.top.destroy()


# app class (класс приложения)
class App(Tk):
    def __init__(self, buttons, plotter, commands, entries):
        super().__init__()
        self.buttons = buttons
        self.plotter = plotter
        self.commands = commands
        self.entries = entries
        self.entries.set_parent_window(self)
        self.plotter.set_parent_window(self)
        self.commands.set_parent_window(self)
        self.buttons.set_parent_window(self)

    def add_hotkey(self, command_name, *args, **kwargs):
        hot_key = kwargs.get('hot_key')
        if hot_key:
            kwargs.pop('hot_key')
        callback = partial(self.commands.get_command_by_name(command_name), *args, **kwargs)
        if hot_key:
            self.bind(hot_key, callback)

    def add_button(self, name, text, command_name, *args, **kwargs):
        hot_key = kwargs.get('hot_key')
        if hot_key:
            kwargs.pop('hot_key')
        callback = partial(self.commands.get_command_by_name(command_name), *args, **kwargs)
        new_button = self.buttons.add_button(name=name, text=text, command=callback)
        if hot_key:
            self.bind(hot_key, callback)
        new_button.pack(fill=BOTH)

    def get_button_by_name(self, name):
        return self.buttons.buttons.get(name)

    def create_menu(self):
        menu = Menu(self)
        self.config(menu=menu)

        file_menu = Menu(menu)
        file_menu.add_command(label="Save as...", command=self.commands.get_command_by_name('save_as'))
        file_menu.add_command(label="Open file", command=self.commands.get_command_by_name('open_file'))
        file_menu.add_command(label="Create template", command=self.commands.get_command_by_name('create_template'))
        menu.add_cascade(label="File", menu=file_menu)
        global template_menu
        template_menu = Menu(menu)
        template_menu.add_command(label="Home", command=self.commands.get_command_by_name('clear_all'))
        menu.add_cascade(label="Templates", menu=template_menu)

    def add_template(self, func):
        template_menu.add_command(label=func, command=lambda: self.commands.draw_func(func))
        # template_menu.add_command(label=func, command= self.commands.draw_func)
        # template_menu.add_command(label=func, command=self.commands.get_command_by_name('draw_func'))
        # template_menu.add_command(label=func, command=self.commands.draw_func())


if __name__ == "__main__":
    # init buttons (создаем кнопки)
    buttons_main = Buttons()
    # init plotter (создаем отрисовщик графиков)
    plotter_main = Plotter()
    # init commands for executing on buttons or hot keys press
    # (создаем команды, которые выполняются при нажатии кнопок или горячих клавиш)
    commands_main = Commands()
    # init entries (создаем текстовые поля)
    entries_main = Entries()
    # command's registration (регистрация команд)
    commands_main.add_command('plot', commands_main.plot)
    commands_main.add_command('clear', commands_main.clear)
    commands_main.add_command('clear_active_plot', commands_main.clear_active_plot)
    commands_main.add_command('clear_all', commands_main.clear_all)
    commands_main.add_command('add_func', commands_main.add_func)
    commands_main.add_command('save_as', commands_main.save_as)
    commands_main.add_command('open_file', commands_main.open_file)
    commands_main.add_command('create_template', commands_main.create_template)
    # commands_main.add_command('home_page', commands_main.home_page)
    commands_main.add_command('draw_func', commands_main.draw_func)
    # init app (создаем экземпляр приложения)
    app = App(buttons_main, plotter_main, commands_main, entries_main)
    # init add func button (добавляем кнопку добавления новой функции)
    app.add_button('add_func', 'Добавить функцию', 'add_func', hot_key='<Control-a>')
    app.add_hotkey('clear_active_plot', hot_key='<Control-g>')
    app.add_hotkey('clear_all', hot_key='<Control-x>')
    # init first entry (создаем первое поле ввода)
    entries_main.add_entry()
    app.create_menu()
    # добавил комментарий для коммита
    # application launch (запуск "вечного" цикла приложеня)
    app.mainloop()

