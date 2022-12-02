from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def yes_no_keyboard(prefix) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton("Да", callback_data=f"{prefix}-yes"),
                 InlineKeyboardButton("Нет", callback_data=f"{prefix}-no"))
    return keyboard
