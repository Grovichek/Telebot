from telebot.types import Message
from states.menu_states import MenuStates
from loader import bot
from keyboards.inline.main_menu import main_menu_keyboard
import handlers

from handlers import *

@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
    bot.send_message(message.from_user.id, "Я помогу тебе найти лучший отель если хочешь")
    bot.send_message(message.from_user.id, "Просто нажми на одну из кнопок, а я сделаю всё остальное",
                     reply_markup=main_menu_keyboard())


# @bot.callback_query_handler(func=lambda call: call.data in ('lowprice', 'highprice', 'bestdeal', 'history', 'survey'))
# def select(message: Message) -> None:
#     if message.data == 'lowprice':
#         print('lowprice')
#     elif message.data == 'highprice':
#         print('highprice')
#     elif message.data == 'bestdeal':
#         print('bestdeal')
#     elif message.data == 'history':
#         print('history')
#     elif message.data == 'survey':
#         print('survey')
#         bot.answer_callback_query(message.id, "Запускаю опрос")
#         bot.set_state(message.from_user.id, MenuStates.survey)
