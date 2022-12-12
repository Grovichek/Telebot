from telebot.types import Message, CallbackQuery, InputMediaPhoto
from telegram_bot_calendar import WYearTelegramCalendar
from datetime import date, timedelta
import asyncio

from api_services.hotels.get_detail import get_hotels_detail
from api_services.hotels.get_properties import search_hotels_by_filters
from keyboards.inline.go_back_kb import go_back_kb
from keyboards.inline.hotels_kb import keyboard_for_hotels
from loader import bot
from states.my_states import MainStates
from keyboards.inline.cities_kb import keyboard_for_cities
from keyboards.inline.num_kd import num_keyboard
from keyboards.inline.yes_no_kd import yes_no_keyboard
from api_services.hotels.get_locations import get_cities_by_query

# ТЗ
# Команда /lowprice
# После ввода команды у пользователя запрашивается:
# 1. Город, где будет проводиться поиск.
# 2. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).
# 3. Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”)
#   a. При положительном ответе пользователь также вводит количество необходимых фотографий (не больше заранее
#   определённого максимума)

# Команда /highprice
# После ввода команды у пользователя запрашивается:
# 1. Город, где будет проводиться поиск.
# 2. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).
# 3. Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”)
#   a. При положительном ответе пользователь также вводит количество необходимых фотографий (не больше заранее
#   определённого максимума)

# Команда /bestdeal
# После ввода команды у пользователя запрашивается:
# 1. Город, где будет проводиться поиск.
# 2. Диапазон цен.
# 3. Диапазон расстояния, на котором находится отель от центра.
# 4. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).
# 5. Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”)
#   a. При положительном ответе пользователь также вводит количество необходимых фотографий (не больше заранее
#   определённого максимума)

# Команда /history
# После ввода команды пользователю выводится история поиска отелей. Сама история содержит:
# 1. Команду, которую вводил пользователь.
# 2. Дату и время ввода команды.
# 3. Отели, которые были найдены.


MAX_NUM_OF_RESULTS = 15
MAX_NUM_OF_PHOTOS = 10

# TODO Если на любом этапе сценария ввести что-то, сценарий начинается с начала (с поиска городов)
#  не смотря на состояния пользователя


@bot.callback_query_handler(func=lambda call: call.data.startswith('start_'))
def start(call: CallbackQuery) -> None:
    """Запуск сценария и выбор типа сортировки, запрос города"""
    with bot.retrieve_data(call.from_user.id) as data:
        if call.data.lstrip('start_') == 'low_price':
            data['sort'] = 'PRICE_LOW_TO_HIGH'
            word = 'дешёвые'
        elif call.data.lstrip('start_') == 'high_price':
            data['sort'] = 'PRICE_HIGH_TO_LOW'
            word = 'дорогие'
        data['main_msg'] = bot.edit_message_text(f'Хорошо, в каком городе мне поискать {word} отели?',
                                                 call.message.chat.id,
                                                 call.message.message_id)
    bot.set_state(call.from_user.id, MainStates.get_city)


@bot.message_handler(state=MainStates.get_city)
def get_city(msg: Message):
    """Вывод клавиатуры с найденными городами для уточнения"""
    with bot.retrieve_data(msg.from_user.id) as data:
        bot.delete_message(msg.chat.id, data['main_msg'].message_id)
        data['main_msg'] = bot.send_message(msg.chat.id, 'Нужно подумать')
    try:
        cities = get_cities_by_query(msg.text)
    except:
        cities = 0
    if cities:
        bot.edit_message_text('Выберите из списка подходящий вариант',
                              msg.chat.id,
                              data['main_msg'].message_id,
                              reply_markup=keyboard_for_cities(iter=cities, prefix='get-city'))
    else:
        bot.edit_message_text('Ничего не найдено, уточните ваш запрос',
                              msg.chat.id,
                              data['main_msg'].message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('get-city'))
def get_dates(call: CallbackQuery):
    """Сохранение выбранного города, вывод клавиатуры для выбора даты заселения"""
    with bot.retrieve_data(call.from_user.id) as data:
        data['region_id'] = call.data.lstrip('get-city')
    calendar, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()
    bot.edit_message_text('Выберите дату предполагаемого заселения в отель:', call.message.chat.id,
                          call.message.message_id, reply_markup=calendar)
    bot.set_state(call.message.from_user.id, MainStates.get_check_in)


@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=1))
def cal(c: CallbackQuery):
    """Сохранение даты заселения, вывод клавиатуры для выбора даты выселения"""
    result, key, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text("Выберите дату предполагаемого заселения в отель:",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(c.message.chat.id) as data:
            data['check_in'] = result
        calendar, step = WYearTelegramCalendar(calendar_id=2, locale='ru', min_date=date.today()).build()
        bot.edit_message_text("Выберите дату предполагаемого выселения из отеля:",
                              c.message.chat.id,
                              c.message.message_id, reply_markup=calendar)
        bot.set_state(c.message.from_user.id, MainStates.get_check_out)


@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=2))
def cal(c: CallbackQuery):
    """Сохранение даты выселение, вывод клавиатуры для запроса количества необходимых результатов"""
    with bot.retrieve_data(c.message.chat.id) as data:
        result, key, step = WYearTelegramCalendar(calendar_id=2,
                                                  locale='ru',
                                                  min_date=data['check_in'] + timedelta(days=1)).process(c.data)
    if not result and key:
        bot.edit_message_text("Выберите дату предполагаемого выселения из отеля:",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(c.message.chat.id) as data:
            data['check_out'] = result
        bot.edit_message_text("Сколько результатов отобразить?",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=num_keyboard(MAX_NUM_OF_RESULTS, 'num_of_results'))
        bot.set_state(c.message.from_user.id, MainStates.get_num_of_results)


@bot.callback_query_handler(func=lambda call: call.data.startswith('num_of_results'))
def get_num_of_results(call: CallbackQuery):
    """Сохранение количества необходимых результатов, вывод клавиатуры с запросом о необходимости загрузки фото"""
    with bot.retrieve_data(call.message.chat.id) as data:
        data['num_of_results'] = int(call.data.lstrip('num_of_results'))
    bot.edit_message_text("Загрузить фото из отелей??",
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=yes_no_keyboard('is_show_photo'))
    bot.set_state(call.message.from_user.id, MainStates.get_is_show_photo)


@bot.callback_query_handler(func=lambda call: call.data.startswith('is_show_photo_yes'))
def yes(call: CallbackQuery):
    """Устанавливает флаг data['is_show_photos'] = True, запрашивает необходимое количество фото"""
    with bot.retrieve_data(call.message.chat.id) as data:
        data['is_show_photos'] = True
        bot.edit_message_text("Сколько фото для каждого отеля загрузить?",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=num_keyboard(MAX_NUM_OF_PHOTOS, 'num_of_photos'))
    bot.set_state(call.message.from_user.id, MainStates.get_num_of_photos)


@bot.callback_query_handler(func=lambda call: call.data.startswith('is_show_photo_no'))
def no(call: CallbackQuery):
    """Устанавливает флаг data['is_show_photos'] = False, вызывает функцию show_results()"""
    with bot.retrieve_data(call.message.chat.id) as data:
        data['is_show_photos'] = False
        data['num_of_photos'] = 0
    bot.set_state(call.message.from_user.id, MainStates.show_result)
    show_results(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('num_of_photos'))
def get_num_of_photos(call: CallbackQuery):
    """Сохраняет необходимое количество фото, вызывает функцию show_results()"""
    with bot.retrieve_data(call.message.chat.id) as data:
        data['num_of_photos'] = int(call.data.lstrip('num_of_photos'))
    bot.set_state(call.message.from_user.id, MainStates.show_result)
    show_results(call.message)


def show_results(msg: Message):
    """Функция для обработки результатов, вывод клавиатуры с найденными отелями"""
    bot.edit_message_text("Нужно немного подождать⏳",
                          msg.chat.id,
                          msg.message_id)
    with bot.retrieve_data(msg.chat.id) as data:
        hotels = search_hotels_by_filters(region_id=data['region_id'],
                                          num_of_results=data['num_of_results'],
                                          check_in_date=data['check_in'],
                                          check_out_date=data['check_out'],
                                          sort=data['sort'])
        results = asyncio.run(get_hotels_detail(hotels=hotels, num_of_images=data['num_of_photos']))
        data['results'] = results
    bot.edit_message_text('Вот что удалось найти',
                          msg.chat.id,
                          msg.message_id,
                          reply_markup=keyboard_for_hotels(results, 'hotel'))


@bot.callback_query_handler(func=lambda call: call.data.startswith('hotel'))
def show_selected_hotel(call: CallbackQuery):
    """Вывод фотографий и карточки выбранного отеля"""
    with bot.retrieve_data(call.message.chat.id) as data:
        for hotel in data['results']:
            if hotel.hotel_id == call.data.lstrip('hotel'):
                bot.delete_message(call.message.chat.id, call.message.message_id)
                # TODO Тут медиа группа отправляется
                data['images'] = bot.send_media_group(call.message.chat.id, [InputMediaPhoto(i) for i in hotel.images])

                bot.send_message(call.message.chat.id,
                                 f"Название отеля - {hotel.hotel_name}\n"
                                 f"Расстояние до центра - {hotel.distance_from_center}\n"
                                 f"Цена за ночь от {hotel.price}\n"
                                 f"Рейтинг - {hotel.reviews}\n"
                                 f"Адресс - {hotel.address}\n"
                                 f"⭐{hotel.star_rating}",
                                 reply_markup=go_back_kb())


@bot.callback_query_handler(func=lambda call: call.data == 'go_back')
def go_back(call: CallbackQuery):
    """Возврат к результатам"""
    with bot.retrieve_data(call.message.chat.id) as data:
        # TODO Тут медиа группа удаляется
        [bot.delete_message(call.message.chat.id, i.message_id) for i in data['images']]

        bot.edit_message_text('Вот что удалось найти',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=keyboard_for_hotels(data['results'], 'hotel'))
