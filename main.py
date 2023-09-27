import json
import matplotlib
import numexpr as ne
import numpy as np

from functools import partial
from tkinter import *
from tkinter.filedialog import asksaveasfile, askopenfilename
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

    def add_entry(self, value=None):
        new_entry = Entry(self.parent_window)

        if value:
            new_entry.insert(0, value)

        new_entry.icursor(0)
        new_entry.focus()
        new_entry.pack()
        self.restore_plot_button()
        self.entries_list.append(new_entry)

    def del_entry(self, entry):
        if entry in self.entries_list:
            self.entries_list.remove(entry)
        entry.destroy()

    def clear_entries(self):
        for entry in self.entries_list:
            entry.destroy()
        self.entries_list.clear()

    def create_entries(self, entries_values):
        for value in entries_values:
            self.add_entry(value)

    def restore_plot_button(self):

        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')

    def delete_entries(self):
        for entry in self.entries_list:
            entry.destroy()
        self.entries_list = []

    def add_entries_with_text(self, list_of_func):
        for func in list_of_func:
            text = StringVar()
            text.set(func)
            new_entry = Entry(self.parent_window, textvariable=text)
            new_entry.pack()
            self.entries_list.append(new_entry)
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

        def restore_state(self):
            file_in = askopenfile(defaultextension=".json")
            tmp_dict = None
            if file_in is not None:
                tmp_dict = json.load(file_in)

            if tmp_dict and 'entries_list' in tmp_dict:
                return tmp_dict['entries_list']

            return []

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

    def is_plot_mode(self):
        plot_button = self.parent_window.get_button_by_name('plot')
        return not (plot_button and plot_button.winfo_ismapped())

    def add_func(self, *args, **kwargs):
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.add_entry()

    def del_func(self, *args, **kwargs):
        entry = self.parent_window.focus_get()
        if not entry or not isinstance(entry, Entry):
            return

        can_delete_entry = True
        if entry.get():
            mw = ModalWindow(self.parent_window, title='Удаление', labeltext='Вы уверены, что хотите удалить функцию?')
            ok_button = Button(master=mw.top, text='Удалить', command=mw.ok)
            cancel_button = Button(master=mw.top, text='Оставить', command=mw.cancel)
            mw.add_button(ok_button)
            mw.add_button(cancel_button)


            self.parent_window.wait_window(mw.top)
            can_delete_entry = mw.result == 1

        if not can_delete_entry:
            return

        self.parent_window.entries.del_entry(entry)

        if self.is_plot_mode():
            self.plot()
        else:
            self.parent_window.entries.restore_plot_button()


    def save_as(self):
        self._state.save_state()
        return self

    def load(self):
        file_in = askopenfilename(defaultextension=".json")
        if file_in is not None:
            with open(file_in, "r") as file:
                tmp_dict = json.load(file)
        self.parent_window.entries.delete_entries()
        self.__forget_canvas()
        self.__forget_navigation()
        self._state.reset_state()
        self._state.list_of_function = tmp_dict['list_of_function']
        self.parent_window.entries.add_entries_with_text(self._state.list_of_function)
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
        self.result = 0
        if len(title) > 0:
            self.top.title(title)
        if len(labeltext) == 0:
            labeltext = 'Default text'
        Label(self.top, text=labeltext).pack()

    def add_button(self, button):
        self.buttons.append(button)
        button.pack(pady=5)

    def cancel(self):
        self.result = 0
        self.top.destroy()

    def ok(self):
        self.result = 1
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
        file_menu.add_command(label="Save as", command=self.commands.get_command_by_name('save_as'))
        file_menu.add_command(label="Open", command=self.commands.get_command_by_name('load'))
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
    commands_main.add_command('del_func', commands_main.del_func)
    commands_main.add_command('save_as', commands_main.save_as)
    commands_main.add_command('load', commands_main.load)
    # init app (создаем экземпляр приложения)
    app = App(buttons_main, plotter_main, commands_main, entries_main)
    # init add func button (добавляем кнопку добавления новой функции)
    app.add_button('add_func', 'Добавить функцию', 'add_func', hot_key='<Control-a>')
    app.add_button('del_func', 'Удалить функцию', 'del_func', hot_key='<Control-d>')
    # init first entry (создаем первое поле ввода)
    entries_main.add_entry()
    app.create_menu()
    app.geometry('600x400+200+100')
    # добавил комментарий для коммита
    # application launch (запуск "вечного" цикла приложеня)
    app.mainloop()
