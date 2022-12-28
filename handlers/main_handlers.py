from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import WYearTelegramCalendar
from datetime import date, timedelta

from config_data.config import MAX_NUM_OF_RESULTS, MAX_NUM_OF_PHOTOS

from exceptions import ApiException
from handlers.history_handlers import history
from handlers.results_processing import results_processing
from keyboards.inline.distance_kb import distance_kb
from loader import bot
from states.my_states import MainStates
from keyboards.inline.cities_kb import keyboard_for_cities
from keyboards.inline.num_kd import num_keyboard
from keyboards.inline.yes_no_kd import yes_no_keyboard
from keyboards.inline.change_price_kb import change_price_kb
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


@bot.callback_query_handler(func=lambda call: call.data.startswith('start'))
def start(call: CallbackQuery) -> None:
    """Запускает выбранный сценарий, запрашивает город"""
    command = call.data.lstrip('start')
    with bot.retrieve_data(call.from_user.id) as data:
        if command == 'history':
            history(call)
        else:
            if command == 'low_price':
                data['sort'], data['command'] = 'PRICE_LOW_TO_HIGH', 'Топ дешёвых отелей'
                string_command = 'дешёвые отели'
            elif command == 'high_price':
                data['sort'], data['command'] = 'PRICE_HIGH_TO_LOW', 'Топ дорогих отелей'
                string_command = 'дорогие отели'
            elif command == 'best_deal':
                data['sort'], data['command'] = 'BEST_DEAL', 'Лучшие предложения'
                string_command = 'лучшие предложения'
            data['main_msg'] = bot.edit_message_text(f'Хорошо, в каком городе мне поискать {string_command}?',
                                                     call.message.chat.id, call.message.message_id)
            bot.set_state(call.from_user.id, MainStates.get_city)


@bot.message_handler(state=MainStates.get_city)
def get_city(msg: Message) -> None:
    """Выводит клавиатуру с найденными городами для уточнения, предлагает повторить ввод в случае неудачи"""
    with bot.retrieve_data(msg.from_user.id) as data:
        bot.delete_message(msg.chat.id, data['main_msg'].message_id)
        data['main_msg'] = bot.send_message(msg.chat.id, 'Нужно подумать')
    try:
        cities = get_cities_by_query(query=msg.text)
        bot.edit_message_text('Выберите из списка подходящий вариант', msg.chat.id, data['main_msg'].message_id,
                              reply_markup=keyboard_for_cities(cities=cities, prefix='get-city'))
    except ApiException:
        bot.edit_message_text('Ничего не найдено, уточните ваш запрос',
                              msg.chat.id, data['main_msg'].message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('get-city'))
def get_price(call: CallbackQuery) -> None:
    """Сохраняет id города, выводит клавиатуру с запросом диапазона цен"""
    with bot.retrieve_data(call.from_user.id) as data:
        data['region_id'] = call.data.lstrip('get-city')
    bot.edit_message_text('Выберите подходящий диапазон цен',
                          call.message.chat.id, call.message.message_id, reply_markup=change_price_kb('price'))
    bot.set_state(call.from_user.id, MainStates.get_price)


@bot.callback_query_handler(func=lambda call: call.data.startswith('price'))
def get_dates_or_distance(call: CallbackQuery) -> None:
    """Сохраняет диапазон цен, выводит клавиатуру с запросом максимальной дистанции от центра или
    запускает выбор дат в зависимости от выбранного ранее сценария"""
    with bot.retrieve_data(call.from_user.id) as data:
        data['min_price'], data['max_price'] = map(int, call.data.lstrip('price').split())
    if data['sort'] == 'BEST_DEAL':
        bot.edit_message_text('Как далеко от центра искать?',
                              call.message.chat.id, call.message.message_id, reply_markup=distance_kb('distance'))
        bot.set_state(call.from_user.id, MainStates.get_distance)
    else:
        data['max_distance'] = 0
        calendar, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()
        bot.edit_message_text('Выберите дату предполагаемого заселения в отель:',
                              call.message.chat.id, call.message.message_id, reply_markup=calendar)
        bot.set_state(call.from_user.id, MainStates.get_check_in)


@bot.callback_query_handler(func=lambda call: call.data.startswith('distance'))
def get_dates(call: CallbackQuery) -> None:
    """Сохраняет максимальную дистанцию от центра, выводит клавиатуру с запросом даты заселения"""
    with bot.retrieve_data(call.from_user.id) as data:
        data['max_distance'] = float(call.data.lstrip('distance'))
    calendar, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()
    bot.edit_message_text('Выберите дату предполагаемого заселения в отель:',
                          call.message.chat.id, call.message.message_id, reply_markup=calendar)
    bot.set_state(call.from_user.id, MainStates.get_check_in)


@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=1))
def cal(c: CallbackQuery) -> None:
    """Сохраняет дату заселения, выводит клавиатуру для выбора даты выселения"""
    result, key, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text("Выберите дату предполагаемого заселения в отель:",
                              c.message.chat.id, c.message.message_id, reply_markup=key)
    elif result:
        with bot.retrieve_data(c.message.chat.id) as data:
            data['check_in'] = result
        calendar, step = WYearTelegramCalendar(calendar_id=2, locale='ru', min_date=date.today()).build()
        bot.edit_message_text("Выберите дату предполагаемого выселения из отеля:",
                              c.message.chat.id, c.message.message_id, reply_markup=calendar)
        bot.set_state(c.from_user.id, MainStates.get_check_out)


@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=2))
def cal(c: CallbackQuery) -> None:
    """Сохраняет дату выселения, выводит клавиатуру для запроса количества необходимых результатов"""
    with bot.retrieve_data(c.message.chat.id) as data:
        result, key, step = WYearTelegramCalendar(calendar_id=2, locale='ru',
                                                  min_date=data['check_in'] + timedelta(days=1)).process(c.data)
    if not result and key:
        bot.edit_message_text("Выберите дату предполагаемого выселения из отеля:",
                              c.message.chat.id, c.message.message_id, reply_markup=key)
    elif result:
        with bot.retrieve_data(c.message.chat.id) as data:
            data['check_out'] = result
        bot.edit_message_text("Сколько результатов отобразить?",
                              c.message.chat.id, c.message.message_id,
                              reply_markup=num_keyboard(MAX_NUM_OF_RESULTS, 'num_of_results'))
        bot.set_state(c.from_user.id, MainStates.get_num_of_results)


@bot.callback_query_handler(func=lambda call: call.data.startswith('num_of_results'))
def get_num_of_results(call: CallbackQuery) -> None:
    """Сохраняет количество необходимых результатов, выводит клавиатуру с запросом о необходимости загрузки фото"""
    with bot.retrieve_data(call.message.chat.id) as data:
        data['num_of_results'] = int(call.data.lstrip('num_of_results'))
    bot.edit_message_text("Загрузить фото из отелей??",
                          call.message.chat.id, call.message.message_id, reply_markup=yes_no_keyboard('is_show_photo'))
    bot.set_state(call.from_user.id, MainStates.get_is_show_photo)


@bot.callback_query_handler(func=lambda call: call.data.startswith('is_show_photo_yes'))
def yes(call: CallbackQuery) -> None:
    """Запрашивает необходимое количество фото"""
    bot.edit_message_text("Сколько фото для каждого отеля загрузить?",
                          call.message.chat.id, call.message.message_id,
                          reply_markup=num_keyboard(MAX_NUM_OF_PHOTOS, 'num_of_photos'))
    bot.set_state(call.from_user.id, MainStates.get_num_of_photos)


@bot.callback_query_handler(func=lambda call: call.data.startswith('is_show_photo_no'))
def no(call: CallbackQuery) -> None:
    """вызывает функцию results_processing()"""
    with bot.retrieve_data(call.message.chat.id) as data:
        data['num_of_photos'] = 0
    bot.set_state(call.from_user.id, MainStates.show_result)
    results_processing(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('num_of_photos'))
def get_num_of_photos(call: CallbackQuery) -> None:
    """Сохраняет необходимое количество фото, вызывает функцию results_processing()"""
    with bot.retrieve_data(call.message.chat.id) as data:
        data['num_of_photos'] = int(call.data.lstrip('num_of_photos'))
    bot.set_state(call.from_user.id, MainStates.show_result)
    results_processing(call)
