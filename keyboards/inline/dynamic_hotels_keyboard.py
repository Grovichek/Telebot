from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from api_hotels import get_list


def dynamic_hotels_keyboard(content: get_list) -> InlineKeyboardMarkup:
    """динамическая клавиатура для хэндлера lowprice. Принимает словарь от get_list"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.max_row_keys = 1

    for i in content["data"]["propertySearch"]["propertySearchListings"]:
        if 'name' in i:
            keyboard.add(InlineKeyboardButton(i['name'], callback_data=f"hotel-{i['id']}"))
    return keyboard
