from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from api_hotels import get_locations


def dynamic_city_keyboard(content: get_locations, prefix: str) -> InlineKeyboardMarkup:
    """динамическая клавиатура для хэндлера lowprice. Принимает словарь от get_locations"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.max_row_keys = 1

    for i in content['sr']:
        if i['type'] == 'CITY':
            keyboard.add(InlineKeyboardButton(i['regionNames']['displayName'], callback_data=f"{prefix}-{i['gaiaId']}"))
    return keyboard
