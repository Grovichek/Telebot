import json
from datetime import date, timedelta
from typing import NamedTuple
import requests

from config_data.config import HOTELS_API_URL, RAPID_API_KEY
from exceptions import ApiException


class HotelInfo(NamedTuple):
    hotel_id: str
    hotel_name: str
    distance_from_center: str
    price: str
    reviews: str
    address: str
    images: list
    star_rating: str


def search_hotels_by_filters(region_id: str, num_of_results: int, sort: str,
                             check_in_date: date, check_out_date: date) -> list[HotelInfo]:
    """
    Возвращает именованный кортеж HotelInfo
    Описание аргументов в _properties_request()
    """
    properties = _properties_request(region_id=region_id,
                                     num_of_results=num_of_results,
                                     sort=sort,
                                     check_in_date=check_in_date,
                                     check_out_date=check_out_date)
    hotels = []
    for item in properties["data"]["propertySearch"]["properties"]:
        hotels.append(HotelInfo(
            hotel_id=_parse_hotel_id(item),
            hotel_name=_parse_hotel_name(item),
            distance_from_center=_parse_destination(item),
            price=_parse_price(item),
            reviews=_parse_reviews(item),
            address='Не известно',
            images=[],
            star_rating='Не известно'
        ))
    return hotels


def _properties_request(region_id: str, num_of_results: int, sort: str,
                        check_in_date: date, check_out_date: date, adults: int = 1, start_index: int = 0,
                        min_price: int = 1, max_price: int = 500000) -> dict:
    """
    Ищет отели по множеству фильтров
    :param region_id: id региона полученный из get_locations_by_query()
    :param adults: количество взрослых людей
    :param num_of_results: максимальное количество отелей, которое нужно найти
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
        "resultsStartingIndex": start_index,
        "resultsSize": num_of_results,
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
        # with open('hotels.json', 'w') as file:
        #     file.write(json.dumps(response, indent=4, ensure_ascii=False))
        return response


    else:
        raise ApiException(f'Неправильный запрос. код: {response.status_code}')


def _parse_hotel_id(properties: dict):
    """Получение id отеля"""
    try:
        hotel_id = properties['id']
    except:
        hotel_id = None
    return hotel_id


def _parse_hotel_name(properties: dict):
    """Получение названия отеля"""
    try:
        hotel_name = properties['name']
    except:
        hotel_name = None
    return hotel_name


def _parse_destination(properties: dict):
    """Получение расстояния от центра до отеля"""
    try:
        distance_from_center = properties['destinationInfo']['distanceFromDestination']['value']
    except:
        distance_from_center = None
    return distance_from_center


def _parse_price(properties: dict):
    """Получение цены за ночь"""
    try:
        price = properties['price']['strikeOut']['formatted']
    except:
        price = None
    return price


def _parse_reviews(properties: dict):
    """Получение рейтинга отеля"""
    try:
        reviews = properties['reviews']['score']
    except:
        reviews = None
    return reviews

# print(search_hotels_by_filters(region_id='3023', num_of_results=3, sort='PRICE_LOW_TO_HIGH',
#                                check_in_date=date.today(), check_out_date=date.today() + timedelta(days=7)))


# hotel=search_hotels_by_filters(region_id='3023', num_of_results=3, sort='PRICE_LOW_TO_HIGH',
#                                check_in_date=date.today(), check_out_date=date.today() + timedelta(days=7))[0]
#
# hotel._replace(address="wergserthrdtjdkjtjtrjedryk")
# print(hotel)
