from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное инлайн меню бота"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.max_row_keys = 1
    keyboard.add(InlineKeyboardButton("Топ дешёвых отелей", callback_data="lowprice"),
                 InlineKeyboardButton("Топ дорогих отелей", callback_data="highprice"),
                 InlineKeyboardButton("Лучшие предложения", callback_data="bestdeal"),
                 InlineKeyboardButton("История запросов", callback_data="history"),
                 InlineKeyboardButton("Опрос", callback_data="survey"))
    return keyboard
