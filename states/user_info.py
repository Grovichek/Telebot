from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    first_name = State()
    last_name = State()
    age = State()
    country = State()
    city = State()
    phone = State()
