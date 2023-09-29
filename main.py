from Entries import *
from Plotter import *
from Commands import *
from Buttons import *
from App import *

if __name__ == "__main__":
    # init buttons
    buttons_main = Buttons()
    # init plotter
    plotter_main = Plotter()
    # init commands for executing on buttons or hot keys press
    commands_main = Commands()
    # init entries
    entries_main = Entries()

    # command's registration
    commands_main.add_command('plot', commands_main.plot)
    commands_main.add_command('add_func', commands_main.add_func)
    commands_main.add_command('save_as', commands_main.save_as)
    commands_main.add_command('del_func', commands_main.del_func)
    commands_main.add_command('upload_file', commands_main.upload_file)

    # init app
    app = App(buttons_main, plotter_main, commands_main, entries_main)

    # init add func button
    app.add_button('add_func', 'Добавить функцию', 'add_func', hot_key='<Control-a>')
    app.add_button('del_func', 'Удалить функцию', 'del_func', hot_key='<Control-d>')

    # init first entry (создаем первое поле ввода)
    entries_main.add_entry()
    app.create_menu()

    # application launch
    app.mainloop()
