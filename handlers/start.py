from telebot.types import Message

from keyboards.inline.main_menu_kb import main_menu_kb
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.full_name}!\nЧем я могу тебе помочь?",
                     reply_markup=main_menu_kb())
    bot.delete_message(message.chat.id,message.message_id)