from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def num_keyboard(num: int, prefix=str) -> InlineKeyboardMarkup:
    """Динамическая клавиатура, создаёт клавиатуру с 5 кнопками в ряду от 1 до num"""
    keyboard = InlineKeyboardMarkup()
    keyboard.max_row_keys = 5
    keyboard.row_width = 5
    keyboard.add(*(InlineKeyboardButton(str(i), callback_data=f"{prefix}{i}") for i in range(1, num + 1)))

    return keyboard
