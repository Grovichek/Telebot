from telebot.types import CallbackQuery

from keyboards.inline.history_kb import keyboard_for_history
from keyboards.inline.hotels_kb import keyboard_for_hotels
from loader import bot
from database.models.base import *


def history(call: CallbackQuery):
    with db:
        user_history = UserHistory.get_history_items(call.from_user.id)
    bot.edit_message_text(f'типа вот',
                          call.message.chat.id, call.message.message_id,
                          reply_markup=keyboard_for_history(prefix='history_item', user_history=user_history))


@bot.callback_query_handler(func=lambda call: call.data.startswith('history_item'))
def get_history(call: CallbackQuery) -> None:
    with db:
        history_item = HistoryContent.get_history_content(history_item=call.data.lstrip('history_item'))
    with bot.retrieve_data(call.from_user.id) as data:
        data['results'] = results = history_item
    bot.edit_message_text(f'Это было найдено ранее',
                          call.message.chat.id, call.message.message_id,
                          reply_markup=keyboard_for_hotels(hotels=results, prefix='hotel'))
