from telebot.types import Message

from loader import bot


# Команда /history
# После ввода команды пользователю выводится история поиска отелей. Сама история содержит:
# 1. Команду, которую вводил пользователь.
# 2. Дату и время ввода команды.
# 3. Отели, которые были найдены.

@bot.message_handler(commands=['history'])
def history(message: Message):
    pass
    # TODO
