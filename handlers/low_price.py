from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import WYearTelegramCalendar

from loader import bot
from states.my_states import MainStates
from keyboards.inline.dynamic_city_keyboard import dynamic_keyboard
from api_services.hotels.get_locations import get_cities_by_query
from datetime import date
from exceptions import ApiException

MAX_NUM_OF_RESULTS = 10
MAX_NUM_OF_PHOTOS = 10
SORT = 'PRICE_LOW_TO_HIGH'


# Команда /lowprice
# После ввода команды у пользователя запрашивается:
# 1. Город, где будет проводиться поиск.
# 2. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).
# 3. Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”)
#   a. При положительном ответе пользователь также вводит количество необходимых фотографий (не больше заранее
#   определённого максимума)


@bot.callback_query_handler(func=lambda call: call.data == 'start_low_price')
def start_low_price(call: CallbackQuery) -> None:
    """Запуск сценария low_price"""
    # bot.answer_callback_query(call.id, '👌')
    # global my_chat_id
    # global my_message_id
    # my_chat_id = call.message.chat.id
    # my_message_id = call.message.message_id
    print(call.message.message_id)
    bot.send_message(call.message.chat.id, 'Хорошо, в каком городе мне поискать дешёвые отели?')
    bot.set_state(call.from_user.id, MainStates.city)


@bot.message_handler(state=MainStates.city)
def get_city(msg: Message):
    print("гет сити")
    bot.send_message(msg.chat.id, 'Нужно подумать')
    cities = get_cities_by_query(msg.text)
    bot.send_message(msg.chat.id, 'Уточните', reply_markup=dynamic_keyboard(cities=cities, prefix='get-city'))
    bot.set_state(msg.from_user.id, MainStates.check_in)


@bot.callback_query_handler(func=lambda call: call.data.startswith('get-city'))
def get_dates(call: CallbackQuery):
    with bot.retrieve_data(call.from_user.id) as data:
        data['region_id'] = call.data.lstrip('get-city')
    calendar, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()

    bot.send_message(call.message.chat.id, 'Выберите дату предполагаемого заселения в отель:', reply_markup=calendar)


@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=1))
def cal(c: CallbackQuery):
    result, key, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text("Выберите дату предполагаемого заселения в отель:",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(c.message.chat.id) as data:
            data['check_in'] = result
            print(data['check_in'])
        calendar, step = WYearTelegramCalendar(calendar_id=2, locale='ru', min_date=date.today()).build()
        bot.edit_message_text("Выберите дату предполагаемого выселения из отеля:",
                              c.message.chat.id,
                              c.message.message_id, reply_markup=calendar)


@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=2))
def cal(c: CallbackQuery):
    result, key, step = WYearTelegramCalendar(calendar_id=2, locale='ru', min_date=date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text("Выберите дату предполагаемого выселения из отеля:",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(c.message.chat.id) as data:
            data['check_out'] = result
            print(data['check_out'])
        bot.edit_message_text(f"{data['check_in']}  -  {data['check_out']}",
                              c.message.chat.id,
                              c.message.message_id)
