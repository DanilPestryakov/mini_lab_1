import json
import matplotlib

import numexpr as ne
import numpy as np

from functools import partial
from tkinter import *
from tkinter.filedialog import asksaveasfile, askopenfile

from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

matplotlib.use('TkAgg')


# class for entries storage (класс для хранения текстовых полей)
class Entries:
    def __init__(self):
        self.entries_list = []
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    # adding of new entry (добавление нового текстового поля)
    def add_entry(self, func=''):
        new_entry = Entry(self.parent_window)
        new_entry.icursor(0)
        new_entry.focus()
        new_entry.pack()
        new_entry.insert(0, func)
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')
        self.entries_list.append(new_entry)

    # clearing the input line from the text (очистка строки ввода от текста)
    def clear_entry(self):
        focus_entry = self.parent_window.focus_get()
        if type(focus_entry) == Entry: focus_entry.delete(0, END)

    # deleting the active input line (удаление активной строки ввода)
    def delete_entry(self):
        focus_entry = self.parent_window.focus_get()
        if type(focus_entry) == Entry:
            if focus_entry.get() != '':
                # a pop-up window with a warning (всплывающее окно с предупреждением)
                mw = ModalWindow(self.parent_window, title='Удаление строки ввода',
                                 labeltext='В строке уже есть данные.\n Вы уверены, что хотите удалить строку ввода?')
                callback = partial(mw.continue_deleting_entry, entry=focus_entry, entries_list=self.entries_list)
                yes_button = Button(master=mw.top, text='Да', command=callback)
                no_button = Button(master=mw.top, text='Нет', command=mw.cancel)
                mw.add_button(yes_button)
                mw.add_button(no_button)
            else:
                focus_index=self.entries_list.index(focus_entry)
                self.entries_list.pop(focus_index).destroy()
            plot_button = self.parent_window.get_button_by_name('plot')
            if plot_button:
                plot_button.pack_forget()
            self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')

    # deleting all input lines (удаление всех строк ввода)
    def delete_all_entries(self):
        mw = ModalWindow(self.parent_window, title='Удаление всех строк ввода',
                         labeltext='Вы уверены, что хотите удалить все строки ввода?')
        callback = partial(mw.continue_deleting_all_entries, entries_list=self.entries_list)
        yes_button = Button(master=mw.top, text='Да', command=callback)
        no_button = Button(master=mw.top, text='Нет', command=mw.cancel)
        mw.add_button(yes_button)
        mw.add_button(no_button)

        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')

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

    def add_func(self, *args, **kwargs):
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.add_entry()

    def clear_func(self, *args, **kwargs):
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.clear_entry()

    def delete_the_input_line(self, *args, **kwargs):
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.delete_entry()

    def delete_all_of_the_input_lines(self, *args, **kwargs):
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.delete_all_entries()

    def upload_a_saved_file(self):
        file = askopenfile()
        if file != None:
            loaded_file = json.load(file)
            for entry in self.parent_window.entries.entries_list:
                entry.destroy()
            self.parent_window.entries.entries_list=[]
            for func in loaded_file['list_of_function']:
                self.parent_window.entries.add_entry(func)
            self.parent_window.commands.plot()

    def save_as(self):
        self._state.save_state()
        return self


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

    def continue_deleting_entry(self, entry, entries_list):
        self.top.destroy()
        entry.delete(0, END)
        entries_list.pop(entries_list.index(entry)).destroy()

    def continue_deleting_all_entries(self, entries_list):
        self.top.destroy()
        number_of_entry = len(entries_list)
        for i in range(number_of_entry):
            if type(entries_list[0]) == Entry:
                entries_list[0].delete(0, END)
                entries_list.pop(0).destroy()

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
        file_menu.add_command(label="Load file", command=self.commands.get_command_by_name('upload_a_saved_file'))
        menu.add_cascade(label="File", menu=file_menu)


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
    commands_main.add_command('add_func', commands_main.add_func)
    commands_main.add_command('clear_func', commands_main.clear_func)
    commands_main.add_command('delete_the_input_line', commands_main.delete_the_input_line)
    commands_main.add_command('delete_all_of_the_input_lines', commands_main.delete_all_of_the_input_lines)
    commands_main.add_command('upload_a_saved_file', commands_main.upload_a_saved_file)
    commands_main.add_command('save_as', commands_main.save_as)
    # init app (создаем экземпляр приложения)
    app = App(buttons_main, plotter_main, commands_main, entries_main)
    # init add func button (добавляем кнопку добавления новой функции)
    app.add_button('add_func', 'Добавить функцию', 'add_func', hot_key='<Control-a>')
    app.add_button('delete_the_input_line', 'Удалить строку ввода', 'delete_the_input_line', hot_key='<Control-b>')
    app.add_button('delete_all_of_the_input_lines', 'Удалить все строки ввода', 'delete_all_of_the_input_lines', hot_key='<Control-d>')
    app.add_button('clear_func', 'Очистить поле ввода', 'clear_func', hot_key='<Control-e>')
    # init first entry (создаем первое поле ввода)
    entries_main.add_entry()
    app.create_menu()
    # application launch (запуск "вечного" цикла приложеня)
    app.mainloop()
