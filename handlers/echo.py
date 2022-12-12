from telebot.types import Message

from loader import bot

#  TODO при включении эхо, бот перестаёт реагировать на команды (/start,/help)
# @bot.message_handler(content_types=['text'])
# def bot_echo(message: Message):
#     bot.reply_to(message, "Эхо без состояния или фильтра.\nСообщение:"
#                           f"{message.text}")
