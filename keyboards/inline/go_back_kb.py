from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def go_back_kb() -> InlineKeyboardMarkup:
    """Возвращает к списку результатов"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Вернуться к списку", callback_data=f"go_back"))
    return keyboard
