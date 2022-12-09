from loader import bot
import handlers
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_default_commands
from database.crud import create_db_users, create_db_history

if __name__ == '__main__':
    create_db_users()
    create_db_history()
    set_default_commands(bot)
    bot.add_custom_filter(StateFilter(bot))
    bot.infinity_polling()
