import matplotlib

from src.app import App
from src.buttons import Buttons
from src.commands import Commands
from src.entries import Entries
from src.plotter import Plotter

matplotlib.use('TkAgg')

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
    # init app (создаем экземпляр приложения)
    app = App(buttons_main, plotter_main, commands_main, entries_main)
    # init add func button (добавляем кнопку добавления новой функции)
    app.add_button('add_func', 'Добавить функцию', 'add_func', hot_key='<Control-a>')
    # init first entry (создаем первое поле ввода)
    entries_main.add_entry()
    app.create_menu()
    # добавил комментарий для коммита
    # application launch (запуск "вечного" цикла приложеня)
    app.mainloop()
