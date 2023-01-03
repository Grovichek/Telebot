import os

from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

MAX_NUM_OF_RESULTS = 15  # Максимальное количество отображаемых результатов
MAX_NUM_OF_PHOTOS = 10  # Максимальное количество отображаемых фотографий (не более 10)

HISTORY_SIZE = 5  # Размер истории просмотров

HOTELS_API_URL = 'https://hotels4.p.rapidapi.com'
BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
)
