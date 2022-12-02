from telebot.handler_backends import State, StatesGroup


class SearchStates(StatesGroup):
    city = State()
    count_photos = State()
    count_results = State()
    show_results = State()
