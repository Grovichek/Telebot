from telebot.types import Message

from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message):
    bot.reply_to(message, f'К сожалению я еще не знаю что означает "{message.text}"\n'
                          f'всё чему меня научили описано тут: /help')
