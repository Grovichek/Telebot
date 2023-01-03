from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def distance_kb(prefix=str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора максимальной дистанции от центра"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 3
    keyboard.add(
        InlineKeyboardButton('До 1км', callback_data=f"{prefix}{'1'}"),
        InlineKeyboardButton('До 3км', callback_data=f"{prefix}{'3'}"),
        InlineKeyboardButton('До 5км', callback_data=f"{prefix}{'5'}"),
        InlineKeyboardButton('До 7км', callback_data=f"{prefix}{'7'}"),
        InlineKeyboardButton('До 10км', callback_data=f"{prefix}{'10'}"),
        InlineKeyboardButton('Пофиг🤪', callback_data=f"{prefix}{'999'}")
    )

    return keyboard
