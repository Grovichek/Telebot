from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Топ дешёвых отелей", callback_data="startlow_price"),
                 InlineKeyboardButton("Топ дорогих отелей", callback_data="starthigh_price"),
                 InlineKeyboardButton("Лучшие предложения", callback_data="startbest_deal"),
                 InlineKeyboardButton("История запросов", callback_data="starthistory"))
    return keyboard
