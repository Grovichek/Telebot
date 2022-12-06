from telebot.types import Message

from api_services.hotels.get_detail import get_hotel_images
from api_services.hotels.get_properties import search_hotels_by_filters
from api_services.hotels.get_locations import get_cities_by_query
from loader import bot
from datetime import date, timedelta


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
# @bot.message_handler(state=None)
# def bot_echo(message: Message):
#     bot.reply_to(message, "Эхо без состояния или фильтра.\nСообщение:"
#                           f"{message.text}")
#     city = get_cities_by_query(message.text)
#     print(city[0].city_name)
#     hotels = search_hotels_by_filters(city[0].city_id, 2, 5, 'PRICE_LOW_TO_HIGH', date.today(),
#                                       date.today() + timedelta(7))
#     for i in hotels:
#         print(i.hotel_name)
#         media = get_hotel_images(i.hotel_id, 5)
#         bot.send_media_group(message.chat.id, media)
