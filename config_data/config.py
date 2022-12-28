import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

MAX_NUM_OF_RESULTS = 15
MAX_NUM_OF_PHOTOS = 10

HISTORY_SIZE = 2

HOTELS_API_URL = 'https://hotels4.p.rapidapi.com'
BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку")
)
