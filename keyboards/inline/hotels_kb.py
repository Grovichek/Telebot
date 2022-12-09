from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from api_services.hotels.get_properties import HotelInfo


def keyboard_for_hotels(iter: list[HotelInfo], prefix=str) -> InlineKeyboardMarkup:
    """Динамическая клавиатура, создаёт кнопки для каждого найденного города"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 8

    keyboard.row_width = 1
    for hotel in iter:
        keyboard.add(InlineKeyboardButton(f"⭐️{hotel.star_rating}   {hotel.hotel_name}",
                                          callback_data=f"{prefix}{hotel.hotel_id}"))
    keyboard.max_row_keys = 3
    keyboard.row_width=3
    keyboard.add(InlineKeyboardButton('К результатам', callback_data='1', ),
                 InlineKeyboardButton('В меню', callback_data=2),
                 InlineKeyboardButton('Ещё', callback_data=3)
                 )
    return keyboard
