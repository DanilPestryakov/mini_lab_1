import json
from tkinter import messagebox

import matplotlib

import numexpr as ne
import numpy as np

from functools import partial
from tkinter import *
from tkinter.filedialog import asksaveasfile, askopenfilename

from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

matplotlib.use('TkAgg')


# class for entries storage (класс для хранения текстовых полей)
class Entries:
    def __init__(self):
        self.remove_entries = None
        self.set_active_entry = None
        self.delete_active_entry = None
        self.add_entry = None
        self.entries_list = []
        self.parent_window = None
        self.active_entry = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

        # adding of new entry (добавление нового текстового поля)
        def add_entry():
            new_entry = Entry(self.parent_window)
            new_entry.icursor(0)
            new_entry.focus()
            new_entry.pack()
            new_entry.bind('<FocusIn>', self.set_active_entry)  # Bind a handler when receiving focus
            plot_button = self.parent_window.get_button_by_name('plot')
            if plot_button:
                plot_button.pack_forget()
            self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')
            self.entries_list.append(new_entry)

        # method for deleting the active entry (метод для удаления активного текстового поля)
        def delete_active_entry():
            if self.active_entry:
                if self.active_entry.get().strip() == '':
                    self.active_entry.destroy()
                    self.entries_list.remove(self.active_entry)
                    self.active_entry = None
                    self.parent_window.commands.plot()
                else:
                    response = messagebox.askquestion("Deletion information",
                                                      "Are you sure you want to delete the field?")
                    if response == "yes":
                        self.active_entry.destroy()
                        self.entries_list.remove(self.active_entry)
                        self.active_entry = None
                        self.parent_window.commands.plot()

        def remove_entries(self):
            for i in range(len(self.entries_list)):
                self.entries_list.pop().destroy()

        # Method to set active text field
        def set_active_entry(event):
            self.active_entry = event.widget

        # Bind methods to a class instance
        self.add_entry = add_entry
        self.delete_active_entry = delete_active_entry
        self.set_active_entry = set_active_entry
        self.remove_entries = remove_entries


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

        def download_from_state(self):
            file_path = askopenfilename(filetypes=[("JSON Files", "*.json")])
            if file_path:
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        # Обработайте загруженные данные, например:
                        list_of_function = data.get('list_of_function', [])
                        return list_of_function
                        # Далее, восстановите состояние приложения на основе данных
                        # Например, установите значения полей и постройте графики.
                except Exception as e:
                    # Обработка ошибок при загрузке данных из файла
                    print(f"Ошибка при загрузке данных из файла: {str(e)}")

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

    def delete_entry(self):
        self.parent_window.entries.deiete_active_entry()

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

    def save_as(self):
        self._state.save_state()
        return self

    def download_from(self):
        self.parent_window.entries.remove_entries(self.parent_window.entries)
        list_of_funcs = self._state.download_from_state()
        for func in list_of_funcs:
            new_entry = Entry(self.parent_window)
            new_entry.insert(0, func)
            new_entry.bind('<FocusIn>', self.parent_window.entries.set_active_entry)
            new_entry.pack()
            self.parent_window.entries.entries_list.append(new_entry)
            self.plot()


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
        self.geometry("800x600")

        delete_active_entry_button = self.buttons.add_button('delete', 'Delete',
                                                             self.entries.delete_active_entry)
        delete_active_entry_button.pack(fill=BOTH)

        # Bind the delete_active_entry method to a key "Ctrl+s"
        self.bind('<Control-s>', self.delete_active_entry)

    def add_button(self, name, text, command_name, *args, **kwargs):
        hot_key = kwargs.get('hot_key')
        if hot_key:
            kwargs.pop('hot_key')
        callback = partial(self.commands.get_command_by_name(command_name), *args, **kwargs)
        new_button = self.buttons.add_button(name=name, text=text, command=callback)
        if hot_key:
            self.bind(hot_key, callback)
        new_button.pack(fill=BOTH)

    def delete_active_entry(self, event):
        self.entries.delete_active_entry()

    def get_button_by_name(self, name):
        return self.buttons.buttons.get(name)

    def create_menu(self):
        menu = Menu(self)
        self.config(menu=menu)

        file_menu = Menu(menu)
        file_menu.add_command(label="Save as...", command=self.commands.get_command_by_name('save_as'))
        file_menu.add_command(label="Download from...", command=self.commands.get_command_by_name('download_from'))
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
    commands_main.add_command('save_as', commands_main.save_as)
    commands_main.add_command('download_from', commands_main.download_from)
    # init app (создаем экземпляр приложения)
    app = App(buttons_main, plotter_main, commands_main, entries_main)
    # init add func button (добавляем кнопку добавления новой функции)
    app.add_button('add_func', 'Добавить функцию', 'add_func', hot_key='<Control-a>')
    # init first entry (создаем первое поле ввода)
    entries_main.add_entry()
    app.create_menu()
    # добавил комментарий для коммита
    # application launch (запуск "вечного" цикла приложеня)
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
