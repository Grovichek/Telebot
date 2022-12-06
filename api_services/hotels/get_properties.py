import json
from datetime import date, timedelta
from typing import NamedTuple
import requests

from config_data.config import HOTELS_API_URL, RAPID_API_KEY
from exceptions import ApiException


class Hotel(NamedTuple):
    hotel_id: str
    hotel_name: str


def search_hotels_by_filters(region_id: str, adults: int, results_count: int, sort: str,
                             check_in_date: date, check_out_date: date) -> list[Hotel]:
    properties = _properties_request(region_id=region_id, adults=adults, results_count=results_count, sort=sort,
                                     check_in_date=check_in_date, check_out_date=check_out_date, )
    hotels = _parse_list_hotels(properties=properties)
    return hotels


def _properties_request(region_id: str, adults: int, results_count: int, sort: str,
                        check_in_date: date, check_out_date: date,
                        min_price: int = 1, max_price: int = 10000) -> dict:
    """
    Ищет отели по множеству фильтров
    :param region_id: id региона полученный из get_locations_by_query()
    :param adults: количество взрослых людей
    :param results_count: максимальное количество отелей, которое нужно найти
    :param sort: ключ сортировки PRICE_RELEVANT (Цена + наш выбор), REVIEW (Оценка гостей),
                                DISTANCE (Расстояние от центра города),
                                PRICE_LOW_TO_HIGH (цена), PROPERTY_CLASS (количество звезд),RECOMMENDED (Рекомендовано)
    :param check_in_date: Дата заселения
    :param check_out_date: Дата выселения
    :param min_price: минимальная цена за ночь
    :param max_price: максимальная цена за ночь
    :return: Сохраняет результат в файл data/list_of_hotels.json
    """

    url = f"{HOTELS_API_URL}/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": region_id},
        "checkInDate": {
            "day": check_in_date.day,
            "month": check_in_date.month,
            "year": check_in_date.year
        },
        "checkOutDate": {
            "day": check_out_date.day,
            "month": check_out_date.month,
            "year": check_out_date.year
        },
        "rooms": [
            {
                "adults": adults,
                "children": []
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": results_count,
        "sort": sort,
        "filters": {"price": {
            "max": max_price,
            "min": min_price
        }}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    try:
        response = requests.request("POST", url, json=payload, headers=headers, timeout=10)

    except:
        raise ApiException('Время истекло')

    if response.status_code == requests.codes.ok:
        response = json.loads(response.text)
        return response
        # with open('hotels.json', 'w') as file:
        #     file.write(json.dumps(response, indent=4, ensure_ascii=False))

    else:
        raise ApiException(f'Неправильный запрос. код: {response.status_code}')


def _parse_list_hotels(properties: _properties_request) -> list[Hotel]:
    """Принимает словарь от _properties_request(), возвращает список именованных кортежей типа
    [Hotel(hotel_id='2528760', hotel_name='Cressy')]"""
    results = []
    for hotel in properties["data"]["propertySearch"]["properties"]:
        results.append(Hotel(hotel_id=hotel["id"], hotel_name=hotel["name"]))
    if results:
        return results
    raise ApiException('Не найдено ни одного отеля')


# print(search_hotels_by_filters(region_id='3023', adults=1, results_count=3, sort='PRICE_LOW_TO_HIGH',
#                                check_in_date=date.today(), check_out_date=date.today() + timedelta(days=7)))
