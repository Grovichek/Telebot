from typing import NamedTuple
import json
import requests

from config_data.config import HOTELS_API_URL, RAPID_API_KEY
from exceptions import ApiException


class City(NamedTuple):
    city_id: int
    city_name: str


def get_cities_by_query(query: str) -> list[City]:
    """
    :param query: строка для поиска
    :return: список экземпляров City
    """
    locations = _locations_request(query)
    cities = _parse_cities(locations)
    return cities


def _locations_request(query: str) -> dict:
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
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        # TODO Удалить перед сдачей
        ###################################################################################
        response_count = response.headers['X-RateLimit-Requests-Remaining']
        print('Остаток запросов:', response_count)
        ###################################################################################

    except requests.ConnectTimeout:
        raise ApiException(ApiException.timeout_error)
    if response.status_code == requests.codes.ok:
        response = json.loads(response.text)
        if response['rc'] == 'OK':
            return response
        else:
            raise ApiException(ApiException.no_result)
    else:
        raise ApiException(f'{ApiException.bad_request} код: {response.status_code}')


def _parse_cities(locations: dict) -> list[City]:
    """
    :param locations: json с сервера
    :return: Список именованных кортежей City
    """
    result = list()
    for city in locations["sr"]:
        if city["type"] == "CITY":
            result.append(City(city_id=city["gaiaId"], city_name=city["regionNames"]["displayName"]))
    if result:
        return result
    else:
        raise ApiException(ApiException.no_result)
