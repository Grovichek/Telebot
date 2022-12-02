from telebot.handler_backends import State, StatesGroup


class MenuStates(StatesGroup):
    home = State()
    survey = State()
    lowprice = State()
