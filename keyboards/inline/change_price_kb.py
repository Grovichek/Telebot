from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def change_price_kb(prefix=str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.max_row_keys = 3
    keyboard.row_width = 3
    keyboard.add(
        InlineKeyboardButton('Дешевле $50', callback_data=f"{prefix}{'1 50'}"),
        InlineKeyboardButton('$50 - $100', callback_data=f"{prefix}{'50 100'}"),
        InlineKeyboardButton('$100 - $150', callback_data=f"{prefix}{'100 150'}"),
        InlineKeyboardButton('$150 - $200', callback_data=f"{prefix}{'150 200'}"),
        InlineKeyboardButton('$200 - $250', callback_data=f"{prefix}{'200 250'}"),
        InlineKeyboardButton('$250 - $300', callback_data=f"{prefix}{'250 300'}"),
        InlineKeyboardButton('Дороже $300', callback_data=f"{prefix}{'300 99999'}")
    )

    return keyboard
