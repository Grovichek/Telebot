from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Топ дешёвых отелей", callback_data="start_low_price"),
                 InlineKeyboardButton("Топ дорогих отелей", callback_data="start_high_price"),
                 InlineKeyboardButton("Лучшие предложения", callback_data="start_best_deal"),
                 InlineKeyboardButton("История запросов", callback_data="start_history"))
    return keyboard
