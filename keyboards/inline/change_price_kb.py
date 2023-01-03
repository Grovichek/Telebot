from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def change_price_kb(prefix=str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора диапазона цен"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 3
    keyboard.add(
        InlineKeyboardButton('Дешевле $75', callback_data=f"{prefix}{'1 75'}"),
        InlineKeyboardButton('$75 - $125', callback_data=f"{prefix}{'75 125'}"),
        InlineKeyboardButton('$125 - $175', callback_data=f"{prefix}{'125 175'}"),
        InlineKeyboardButton('$175 - $225', callback_data=f"{prefix}{'175 225'}"),
        InlineKeyboardButton('$225 - $300', callback_data=f"{prefix}{'225 300'}"),
        InlineKeyboardButton('Дороже $300', callback_data=f"{prefix}{'300 99999'}")
    )

    return keyboard
