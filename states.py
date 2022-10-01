from aiogram.dispatcher.filters.state import StatesGroup, State

class UrlEnter(StatesGroup):
    Url_input = State()
    Url_out = State()


class MenuCompanies(StatesGroup):
    Menu1= State()
    Menu1_out=State()




