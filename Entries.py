from tkinter import Entry, Button
from ModalWindow import ModalWindow


# class for entries storage (класс для хранения текстовых полей)
class Entries:
    def __init__(self):
        self.entries_list = []
        self.parent_window = None

    def __check_plot_but(self):
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    # adding of new entry (добавление нового текстового поля)
    def add_entry(self, function=""):
        new_entry = Entry(self.parent_window)
        new_entry.icursor(0)
        new_entry.focus()
        new_entry.pack()
        new_entry.insert(0, function)
        self.__check_plot_but()
        self.entries_list.append(new_entry)

    def add_entries_from_json(self, list_of_function):
        for func in list_of_function:
            self.add_entry(function=func)
        self.__check_plot_but()

    def ask_to_del(self):
        entry = self.parent_window.focus_get()
        # if any label is not active
        if entry not in self.entries_list:
            self.__check_plot_but()
            return

        text = entry.get()
        # if active label is empty
        if len(text.strip()) == 0:
            self.del_entry(entry)
            self.__check_plot_but()
            return

        mw = ModalWindow(self.parent_window, title='Delete', labeltext='Точно удалить функцию?')
        yes_button = Button(master=mw.top, text='Yes', command=mw.cancel)
        no_button = Button(master=mw.top, text='No', command=mw.cancel)
        mw.add_button(yes_button)
        mw.add_button(no_button)

        yes_button.bind('<Button-1>', lambda event: self.del_entry(entry))
        no_button.bind('<Button-1>', lambda event: self.__check_plot_but())
        self.parent_window.wait_window(mw.top)

    def del_entry(self, entry):
        entry.destroy()
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()

        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')
        self.entries_list.remove(entry)
