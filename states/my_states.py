from telebot.handler_backends import State, StatesGroup


class MainStates(StatesGroup):
    city = State()
    check_in=State()
    check_out=State()