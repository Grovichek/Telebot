from keyboards.inline.main_menu import main_menu_keyboard
from keyboards.inline.yes_no import yes_no_keyboard
from keyboards.reply.phone import request_phone
from loader import bot
from states.user_info import UserInfoState
from telebot.types import Message, ReplyKeyboardRemove
from database.crud import User
from database import crud
import re


@bot.callback_query_handler(func=lambda call: call.data == 'survey')
def survey(message: Message) -> None:
    bot.answer_callback_query(message.id, "👌")
    if message.from_user.id in User:
        bot.send_message(message.from_user.id, 'Вы уже проходили этот опрос')
        bot.send_message(message.from_user.id, 'Хотите обновить свои данные?',
                         reply_markup=yes_no_keyboard('survey'))

    else:
        bot.set_state(message.from_user.id, UserInfoState.first_name)
        bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}!')
        bot.send_message(message.from_user.id, f'Давай познакомимся поближе!')
        bot.send_message(message.from_user.id, f'Я запрошу у тебя кое-какую информацию, '
                                               f'что-бы потом её продать на чёрном рынке')
        bot.send_message(message.from_user.id, f'Для начала введи своё имя')


@bot.callback_query_handler(func=lambda call: call.data == 'survey-yes')
def yes(message: Message):
    bot.send_message(message.from_user.id, 'Ок, давай начнём с твоего имени')
    bot.set_state(message.from_user.id, UserInfoState.first_name)


@bot.callback_query_handler(func=lambda call: call.data == 'survey-no')
def no(message: Message) -> None:
    bot.set_state(message.from_user.id, 0)
    bot.send_message(message.from_user.id, 'Чем ещё я могу тебе помочь?', reply_markup=main_menu_keyboard())


@bot.message_handler(state=UserInfoState.first_name)
def get_fname(message: Message) -> None:
    if re.match('^[A-Za-zА-ЯЁа-яё-]+?$', message.text):
        if len(message.text) < 30:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['first name'] = message.text.capitalize()
                print(data['first name'])

            bot.reply_to(message, 'Отличное имя! 👍')
            bot.send_message(message.from_user.id, 'Теперь скажи мне свою фамилию')
            bot.set_state(message.from_user.id, UserInfoState.last_name, message.chat.id)
        else:
            bot.reply_to(message, 'Ну не бывает таких длинных имён')
    else:
        bot.reply_to(message, 'Ты меня недооцениваешь! 😏')
        bot.send_message(message.from_user.id, 'Я уже маленько умею читать 😉')
        bot.send_message(message.from_user.id, 'Имя может состоять только из букв и иногда дефиса')
        bot.send_message(message.from_user.id, 'Давай еще разок, только в этот раз без обмана 🧐')


@bot.message_handler(state=UserInfoState.last_name)
def get_lname(message: Message) -> None:
    if re.match('^[A-Za-zА-ЯЁа-яё-]+?$', message.text):
        if len(message.text) < 30:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['last name'] = message.text.capitalize()
                print(data['last name'])

            bot.reply_to(message, 'Ага сохранено 👍')
            bot.send_message(message.from_user.id, 'Теперь возраст')
            bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)
        else:
            bot.reply_to(message, 'Не верю что у тебя такая длинная фамилия')

    else:
        bot.reply_to(message, 'Фамилия как и имя может содержать только буквы и дефис! 😡')


@bot.message_handler(state=UserInfoState.age)
def get_age(message: Message) -> None:
    if message.text.isdigit() and 0 < int(message.text) < 120:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['age'] = int(message.text)
            print(data['age'])
        if int(message.text) < 12:
            bot.reply_to(message, 'Ути малышок 🥰')
            bot.send_message(message.from_user.id, 'Что ж мне делать то с твоими данными?')
            bot.send_message(message.from_user.id, 'Ну ладно, что-нибудь придумаю 😉')
        elif 12 <= int(message.text) <= 50:
            bot.reply_to(message, 'Да ты уже не ребенок!')
            bot.send_message(message.from_user.id, 'Это хорошо 👍')

        bot.send_message(message.from_user.id, 'А в какой стране ты живёшь?')
        bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)
    else:
        bot.reply_to(message, 'Ну сколько можно то? 🤬')
        bot.send_message(message.from_user.id, 'Я прошу возраст, а не сказку на ночь')
        bot.send_message(message.from_user.id, 'Только цифры пожалуйста!')


@bot.message_handler(state=UserInfoState.country)
def get_country(message: Message) -> None:
    if len(message.text) < 20:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['country'] = message.text.capitalize()
            print(data['country'])

        bot.reply_to(message, 'Понятно')
        bot.send_message(message.from_user.id, 'А город?')
        bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    else:
        bot.reply_to(message, 'Разве бываю страны с таким длинным названием? Не думаю')
        bot.send_message(message.from_user.id, 'Попробуй ещё разок')


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    if len(message.text) < 20:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text.capitalize()
            print(data['city'])

        bot.reply_to(message, 'Почти всё!')
        bot.send_message(message.from_user.id, 'Остался только твой номер телефона')
        bot.send_message(message.from_user.id, 'Просто нажми на кнопку и на этом закончим',
                         reply_markup=request_phone())
        bot.set_state(message.from_user.id, UserInfoState.phone, message.chat.id)
    else:
        bot.reply_to(message, 'Разве бываю города с таким длинным названием? Не думаю')
        bot.send_message(message.from_user.id, 'Попробуй ещё разок')


@bot.message_handler(state=UserInfoState.phone, content_types=['contact', 'text'])
def get_phone(message: Message) -> None:
    if message.content_type == 'contact':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['phone'] = message.contact.phone_number
            print(data['phone'])

            if message.from_user.id not in User:
                crud.create_user_by_id(user_id=message.from_user.id,
                                       fname=data['first name'],
                                       lname=data['last name'],
                                       age=data['age'],
                                       country=data['country'],
                                       city=data['city'],
                                       phone=data['phone'])
            else:
                crud.update_user_by_id(user_id=message.from_user.id,
                                       fname=data['first name'],
                                       lname=data['last name'],
                                       age=data['age'],
                                       country=data['country'],
                                       city=data['city'],
                                       phone=data['phone'])

        bot.send_message(message.from_user.id, 'Спасибо за твои личные данные 💋', reply_markup=ReplyKeyboardRemove())
        bot.send_message(message.from_user.id, 'Я сохраню их в своей базе, а когда база подкопится,'
                                               'я её продам и на твой номер телефона могут начать звонить '
                                               'разные нехорошие люди, ну или смски слать')

        bot.send_message(message.from_user.id, f'Вот всё что ты разболтал:\n\n'
                                               f'Имя - {data["first name"]}\n'
                                               f'Фамилия - {data["last name"]}\n'
                                               f'Возраст - {data["age"]}\n'
                                               f'Страна - {data["country"]}\n'
                                               f'Город - {data["city"]}\n'
                                               f'Номер телефона - {data["phone"]}')

        bot.set_state(message.from_user.id, 0, message.chat.id)

    else:
        bot.reply_to(message, 'Ну нажми ты на кнопочку, не останавливаться же за шаг до конца!')
        bot.send_message(message.from_user.id, 'Она вон там 👇, справа от поля ввода')
