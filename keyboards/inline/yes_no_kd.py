from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def yes_no_keyboard(prefix=str) -> InlineKeyboardMarkup:
    """Да/Нет"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Да', callback_data=f'{prefix}_yes'),
                 InlineKeyboardButton('Нет', callback_data=f'{prefix}_no'))
    return keyboard
