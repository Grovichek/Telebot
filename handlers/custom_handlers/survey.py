from keyboards.reply.phone import request_phone
from loader import bot
from states.user_info import UserInfoState
from telebot.types import Message
from database.create_db import User


@bot.message_handler(commands=['survey'])
def survey(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.first_name, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}!')
    bot.send_message(message.from_user.id, f'Давай познакомимся поближе!')
    bot.send_message(message.from_user.id, f'Я запрошу у тебя кое-какую информацию, '
                                           f'что-бы потом её продать на чёрном рынке')
    bot.send_message(message.from_user.id, f'Для начала введи своё имя')


@bot.message_handler(state=UserInfoState.first_name)
def get_fname(message: Message) -> None:
    if message.text.isalpha():
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
        bot.send_message(message.from_user.id, 'Я умею отличать буквы от цифр, а имя не может содержать цифры! 😉')
        bot.send_message(message.from_user.id, 'Давай еще разок, только в этот раз без обмана 🧐')


@bot.message_handler(state=UserInfoState.last_name)
def get_lname(message: Message) -> None:
    if message.text.isalpha():
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
        bot.reply_to(message, 'Фамилия не может содержать цифры! 😡')


@bot.message_handler(state=UserInfoState.age)
def get_age(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['age'] = int(message.text)
            print(data['age'])
        if int(message.text) > 10:
            bot.reply_to(message, 'Да ты уже не ребенок!')
            bot.send_message(message.from_user.id, 'Это хорошо 👍')
        elif int(message.text) > 120:
            bot.reply_to(message, 'Ты точно с нашей планеты? наши столько не живут')
        else:
            bot.reply_to(message, 'Ути малышок 🥰')
            bot.send_message(message.from_user.id, 'Что ж мне делать то с твоими данными?')
            bot.send_message(message.from_user.id, 'Ну ладно, что-нибудь придумаю 😉')
        bot.send_message(message.from_user.id, 'А в какой стране ты живёшь?')
        bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)
    else:
        bot.reply_to(message, 'Ну сколько можно то?')
        bot.send_message(message.from_user.id, 'Как возраст может состоять из букв? 🤬')
        bot.send_message(message.from_user.id, 'Только цифры!')


@bot.message_handler(state=UserInfoState.country)
def get_country(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['country'] = message.text.capitalize()
        print(data['country'])

    bot.reply_to(message, 'Понятно')
    bot.send_message(message.from_user.id, 'А город?')
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text.capitalize()
        print(data['city'])

    bot.reply_to(message, 'Почти всё!')
    bot.send_message(message.from_user.id, 'Остался только твой номер телефона')
    bot.send_message(message.from_user.id, 'Просто нажми на кнопку и на этом закончим', reply_markup=request_phone())
    bot.set_state(message.from_user.id, UserInfoState.phone, message.chat.id)


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.phone)
def get_phone(message: Message) -> None:
    if message.content_type == 'contact':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['phone'] = message.contact.phone_number
            print(data['phone'])
            bot.send_message(message.from_user.id, 'Спасибо за твои личные данные 💋')
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
            try:
                User.create(user_id=message.from_user.id, fname=data['first name'], lname=data['last name'],
                            age=data['age'], country=data['country'], city=data['city'], phone=data['phone'])
            except Exception as err:
                print(err)



    else:
        bot.reply_to(message, 'Ну нажми ты на кнопочку, не останавливаться же за шаг до конца!')
        bot.send_message(message.from_user.id, 'Она вон там 👇, справа от поля ввода')
