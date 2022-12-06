from typing import NamedTuple
import json
import requests

from config_data.config import HOTELS_API_URL, RAPID_API_KEY
from exceptions import ApiException


class City(NamedTuple):
    city_id: int
    city_name: str


def get_cities_by_query(query: str) -> list:
    """
    :param query: строка для поиска
    :return: список экземпляров City
    """
    locations = _locations_request(query)
    cities = _parse_cities(locations)
    return cities


def _locations_request(query: get_cities_by_query) -> dict:
    """
    :param query: название города или страны
    :return: ответ сервера
    """
    url = f"{HOTELS_API_URL}/locations/v3/search"

    querystring = {"q": query, "locale": 'ru_RU', "langid": "1033", "siteid": "300000001"}

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)

    except:
        raise ApiException('Время истекло')

    if response.status_code == requests.codes.ok:
        response = json.loads(response.text)
        if response['rc'] == 'OK':
            # with open('locations.json', 'w') as file:
            #     file.write(json.dumps(response, indent=4, ensure_ascii=False))
            return response
        else:
            raise ApiException('Ничего не найдено')
    else:
        raise ApiException(f'Неправильный запрос. код: {response.status_code}')


def _parse_cities(locations: _locations_request) -> list[City]:
    """Принимает словарь от get_locations_by_query(), возвращает список именованных кортежей типа
    [City(city_id='3023', city_name='Рим, Лацио, Италия')]"""

    result = list()
    for city in locations["sr"]:
        if city["type"] == "CITY":
            result.append(City(city_id=city["gaiaId"], city_name=city["regionNames"]["displayName"]))
    if result:
        return result
    else:
        raise ApiException('В списке не найдено городов')


# print(get_cities_by_query('london'))
