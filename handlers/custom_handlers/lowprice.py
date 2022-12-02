from telebot.types import Message
from loader import bot
from states.search_states import SearchStates
from states.menu_states import MenuStates
from api_hotels import get_locations, get_photos
from keyboards.inline.yes_no import yes_no_keyboard
from api_hotels import get_list
from keyboards.inline.dynamic_city_keyboard import dynamic_city_keyboard
from keyboards.inline.dynamic_hotels_keyboard import dynamic_hotels_keyboard
import re


# Команда /lowprice
# После ввода команды у пользователя запрашивается:
# 1. Город, где будет проводиться поиск.
# 2. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).
# 3. Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”)
#   a. При положительном ответе пользователь также вводит количество необходимых фотографий (не больше заранее
#   определённого максимума)


@bot.callback_query_handler(func=lambda call: call.data == 'lowprice')
def lowprice(message: Message) -> None:
    bot.answer_callback_query(message.id, "👌")
    bot.send_message(message.from_user.id, 'Хорошо, в каком городе мне поискать дешёвые отели?')
    bot.set_state(message.from_user.id, SearchStates.city)


@bot.message_handler(state=SearchStates.city)
def get_city(message: Message) -> None:
    if len(message.text) < 30:
        bot.send_message(message.from_user.id, "Мне нужно маленько подумать, подожди пожалуйста")
        r = get_locations(message.text)
        if r:
            bot.send_message(message.from_user.id, 'Выбери подходящий вариант из списка',
                             reply_markup=dynamic_city_keyboard(r, 'city'))
        else:
            bot.send_message(message.from_user.id,
                             'Я не знаю такого города, попробуй ещё разок, может буквы перепутал?')
    else:
        bot.send_message(message.from_user.id, 'Длинновато, давай по короче')


@bot.callback_query_handler(func=lambda call: call.data.startswith('city'))
def get_region_id(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id) as data:
        data['region_id'] = message.data.lstrip('city-')
    bot.send_message(message.from_user.id, 'Отлично! Сколько показать отелей?')
    bot.set_state(message.from_user.id, SearchStates.count_results)


@bot.message_handler(state=SearchStates.count_results)
def get_count_results(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if int(message.text) <= 10:
                data['count_results'] = int(message.text)
            else:
                bot.send_message(message.from_user.id, 'Нее, столько не смогу, покажу десять')
                data['count_results'] = 10
        bot.send_message(message.from_user.id, 'Показать фото найденных отелей?',
                         reply_markup=yes_no_keyboard('show'))
        # TODO Этот хендлер возвращает колбэк, нужно ли для хендлера который его принимает писать состояние?
        #  технически состояние там не нужно, но без него бот остаётся в текущем состоянии и если например
        #  вместо нажатия инлайн кнопок писать что-то в чат будет отрабатывать этот хендлер
        #  как грамотно решить эту проблему? я решил создать дефолтное состояние MenuStates.home
        #  и возвращать состояние к нему когда оно не требуется, но мне кажется это не правильно
        #  -------------
        #  еще вопрос по поводу колбэк хендлеров, я пытался сделать универсальную клавиатуру, чтобы ее можно было
        #  переиспользовать, придумал передавать в нее префикс, это нормальная практика?
    else:
        bot.send_message(message.from_user.id, 'Цифрами пожалуйста')


@bot.callback_query_handler(func=lambda call: call.data == 'show-yes')
def yes(message: Message) -> None:
    bot.set_state(message.from_user.id, SearchStates.count_photos)
    bot.send_message(message.from_user.id, 'Хорошо, сколько фотографий показать для каждого отеля?')


@bot.callback_query_handler(func=lambda call: call.data == 'show-no')
def no(message: Message) -> None:
    bot.set_state(message.from_user.id, SearchStates.show_results)
    show_results(message, False)


@bot.message_handler(state=SearchStates.count_photos)
def get_count_photos(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if int(message.text) <= 5:
                data['count_photos'] = int(message.text)
            else:
                bot.send_message(message.from_user.id, 'Многовато, покажу по пять фоток для каждого')
                data['count_photos'] = 5

        bot.set_state(message.from_user.id, SearchStates.show_results)
        show_results(message, True)

    else:
        bot.send_message(message.from_user.id, 'Цифрами пожалуйста')

# TODO Всё что ниже, еще не придумано.
#  Просьба дать рекомендации по коду и архитектуре, я уже начал тонуть в том что сам же написал, как бы я не старался
#  всё делать аккуратно, чем больше кода, тем больше бардака, мне всё время хочется всё удалить и начать с начала,
#  нужно ли писать документацию к хендлерам? или просто в начале файла описать сценарий?
def show_results(message: Message, photo: bool) -> None:
    bot.send_message(message.from_user.id, 'Погоди чуток')
    with bot.retrieve_data(message.from_user.id) as data:
        r = get_list(region_id=data['region_id'],
                     adults=2,
                     results_size=data['count_results'],
                     sort='PRICE_LOW_TO_HIGH')
    if photo:
        bot.send_message(message.from_user.id, 'тут скоро будут фотки типа этой')
        photo = "https://images.trvl-media.com/lodging/10000000/9210000/9209700/9209612/4d162553.jpg?impolicy=resizecrop&rw=670&ra=fit"

        bot.send_photo(message.from_user.id, photo, caption='подпись')
    else:
        bot.send_message(message.from_user.id, 'тут что-то будет, пока просто кнопки',
                         reply_markup=dynamic_hotels_keyboard(r))
