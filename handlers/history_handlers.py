from telebot.types import CallbackQuery

from keyboards.inline.history_kb import keyboard_for_history
from keyboards.inline.hotels_kb import keyboard_for_hotels
from loader import bot
from database.models.base import *


def history(call: CallbackQuery):
    """Выводит клавиатуру с историей"""
    with db:
        user_history = UserHistory.get_list_of_history_elements(call.from_user.id)
    bot.edit_message_text(f'История ваших запросов',
                          call.message.chat.id, call.message.message_id,
                          reply_markup=keyboard_for_history(prefix='history_item', user_history=user_history))


@bot.callback_query_handler(func=lambda call: call.data.startswith('history_item'))
def get_history(call: CallbackQuery) -> None:
    """Выводит клавиатуру с результатами выбранного ранее элемента истории"""
    with db:
        history_item = HistoryContent.get_list_of_history_content(history_item=call.data.lstrip('history_item'))
    with bot.retrieve_data(call.from_user.id) as data:
        data['results'] = results = history_item
    bot.edit_message_text(f'Это было найдено ранее',
                          call.message.chat.id, call.message.message_id,
                          reply_markup=keyboard_for_hotels(hotels=results, prefix='hotel'))
