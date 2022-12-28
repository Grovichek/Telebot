from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def keyboard_for_history(prefix, user_history) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 8
    keyboard.row_width = 1
    for user_history_item in user_history:
        keyboard.add(InlineKeyboardButton(f"{user_history_item.command},{user_history_item.date}",
                                          callback_data=f"{prefix}{user_history_item.id}"))
    return keyboard
