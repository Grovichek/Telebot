from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from api_services.hotels.get_properties import HotelInfo


def keyboard_for_hotels(iter: list[HotelInfo], prefix=str) -> InlineKeyboardMarkup:
    """Динамическая клавиатура, создаёт кнопки для каждого найденного отеля"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 8

    keyboard.row_width = 1
    for hotel in iter:
        keyboard.add(InlineKeyboardButton(f"⭐️{hotel.star_rating}   {hotel.hotel_name}",
                                          callback_data=f"{prefix}{hotel.hotel_id}"))
    keyboard.max_row_keys = 3
    keyboard.row_width = 3
    keyboard.add(InlineKeyboardButton('В главное меню', callback_data=f"main_menu"),
                 InlineKeyboardButton('Показать ещё', callback_data=f"{prefix}-more_results"))
    return keyboard
