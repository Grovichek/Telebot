from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def request_phone() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('Засветить свой номер', request_contact=True))
    return keyboard
