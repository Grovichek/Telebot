from telebot.types import Message, CallbackQuery
from states.my_states import MainStates

from keyboards.inline.main_menu_kb import main_menu_kb
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(msg: Message):
    bot.set_state(msg.from_user.id, MainStates.main_menu)
    bot.send_message(msg.chat.id, f"Привет, {msg.from_user.full_name}!\nЧем я могу тебе помочь?",
                     reply_markup=main_menu_kb())
    bot.delete_message(msg.chat.id, msg.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def main_menu(call: CallbackQuery) -> None:
    bot.set_state(call.message.from_user.id, MainStates.main_menu)
    bot.send_message(call.message.chat.id, f"Привет, {call.message.from_user.full_name}!\nЧем я могу тебе помочь?",
                     reply_markup=main_menu_kb())
    bot.delete_message(call.message.chat.id, call.message.message_id)
