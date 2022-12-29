import asyncio
from telebot.types import CallbackQuery, InputMediaPhoto

from api_services.hotels.get_detail import get_hotels_detail
from api_services.hotels.get_properties import search_hotels_by_filters
from exceptions import ApiException
from keyboards.inline.go_back_kb import go_back_kb
from keyboards.inline.hotels_kb import keyboard_for_hotels
from keyboards.inline.main_menu_kb import main_menu_kb
from loader import bot
from database.utils import CRUD
from database.common.models import db


def results_processing(call: CallbackQuery) -> None:
    """Функция для обработки результатов, вывод клавиатуры с найденными отелями"""
    bot.edit_message_text("Нужно немного подождать пока я загужу данные⏳",
                          call.message.chat.id, call.message.message_id)
    with bot.retrieve_data(call.message.chat.id) as data:
        try:
            hotels = search_hotels_by_filters(region_id=data['region_id'],
                                              num_of_results=data['num_of_results'],
                                              check_in_date=data['check_in'],
                                              check_out_date=data['check_out'],
                                              sort=data['sort'],
                                              min_price=data['min_price'],
                                              max_price=data['max_price'],
                                              max_distance=data['max_distance'])
        except ApiException:
            bot.edit_message_text('Ничего не найдено, попробуй ещё раз',
                                  call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
        try:
            data['results'] = asyncio.run(get_hotels_detail(hotels=hotels, num_of_images=data['num_of_photos']))
            with db:
                CRUD.create_history_element(db=db, telegram_id=call.from_user.id,
                                            command=data['command'], hotels=data['results'])
                CRUD.delete_last_history_element(db=db, telegram_id=call.from_user.id)
            bot.edit_message_text('Вот что удалось найти:',
                                  call.message.chat.id, call.message.message_id,
                                  reply_markup=keyboard_for_hotels(data['results'], 'hotel'))
        except ApiException:
            bot.edit_message_text('Сервер гонит, попробуй ещё раз',
                                  call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
        except AttributeError:
            bot.edit_message_text('Ничего не найдено, попробуй ещё раз',
                                  call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())


@bot.callback_query_handler(func=lambda call: call.data.startswith('hotel'))
def show_selected_hotel(call: CallbackQuery) -> None:
    """Выводит фотографии и карточку выбранного отеля,
        также выводит клавиатуру с предложением вернуться назад"""
    with bot.retrieve_data(call.message.chat.id) as data:
        for hotel in data['results']:
            if hotel.hotel_id == call.data.lstrip('hotel'):
                if hotel.images:
                    data['images'] = bot.send_media_group(call.message.chat.id,
                                                          [InputMediaPhoto(i) for i in hotel.images])

                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id,
                                 f"Название отеля - ⭐{hotel.star_rating} - {hotel.hotel_name}\n"
                                 f"Расстояние до центра - {hotel.distance_from_center} км\n"
                                 f"Цена за ночь от {hotel.price}\n"
                                 f"Рейтинг - {hotel.reviews}/10\n"
                                 f"Адрес - {hotel.address}",
                                 reply_markup=go_back_kb())


@bot.callback_query_handler(func=lambda call: call.data == 'go_back')
def go_back(call: CallbackQuery) -> None:
    """Возврат к результатам"""
    with bot.retrieve_data(call.message.chat.id) as data:
        try:
            [bot.delete_message(call.message.chat.id, i.message_id) for i in data['images']]
        except KeyError:
            pass
        bot.edit_message_text('Вот что удалось найти',
                              call.message.chat.id, call.message.message_id,
                              reply_markup=keyboard_for_hotels(data['results'], 'hotel'))
