from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    """Главное инлайн меню бота"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.max_row_keys = 1
    keyboard.add(InlineKeyboardButton("Топ дешёвых отелей", callback_data="start_low_price"),
                 InlineKeyboardButton("Топ дорогих отелей", callback_data="start_high_price"),
                 InlineKeyboardButton("Лучшие предложения", callback_data="start_bestdeal"),
                 InlineKeyboardButton("История запросов", callback_data="start_history"))
    return keyboard
