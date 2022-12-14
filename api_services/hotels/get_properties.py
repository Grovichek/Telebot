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
                             check_in_date: date, check_out_date: date,
                             min_price: int, max_price: int, max_distance: float = None) -> list[HotelInfo]:
    """
    Возвращает список именованных кортежей HotelInfo отсортированных одним из 3 способов
    Описание аргументов в _properties_request()
    """
    if sort == 'PRICE_LOW_TO_HIGH':
        properties = _properties_request(region_id=region_id, num_of_results=num_of_results,
                                         check_in_date=check_in_date, check_out_date=check_out_date,
                                         min_price=min_price, max_price=max_price)

    elif sort == 'PRICE_HIGH_TO_LOW':
        properties = _sort_high_to_low(region_id=region_id, num_of_results=num_of_results, check_in_date=check_in_date,
                                       check_out_date=check_out_date, min_price=min_price, max_price=max_price)
    elif sort == 'BEST_DEAL':
        properties = _sort_best_deal(region_id=region_id, num_of_results=num_of_results, check_in_date=check_in_date,
                                     check_out_date=check_out_date, min_price=min_price, max_price=max_price,
                                     max_distance=max_distance)
    else:
        properties = {}
    hotels = []
    for item in properties:
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


def _sort_high_to_low(region_id, num_of_results, check_in_date, check_out_date, min_price, max_price)->list:
    """Сортировка результатов по убыванию цены"""
    properties = _properties_request(region_id=region_id, check_in_date=check_in_date, check_out_date=check_out_date,
                                     min_price=min_price, max_price=max_price)
    results = []
    for hotel in properties[:-num_of_results - 1:-1]:
        results.append(hotel)
    return results


def _sort_best_deal(region_id, num_of_results, check_in_date, check_out_date, min_price, max_price, max_distance)->list:
    """Сортировка результатов по возрастанию цены и удалённости от центра"""
    properties = _properties_request(region_id=region_id, check_in_date=check_in_date, check_out_date=check_out_date,
                                     min_price=min_price, max_price=max_price)
    results = []
    for hotel in properties:
        if max_distance >= _parse_destination(hotel) and len(results) < num_of_results:
            results.append(hotel)
    return results


def _properties_request(region_id: str, check_in_date: date, check_out_date: date, num_of_results: int = 200,
                        adults: int = 1, start_index: int = 0, min_price: int = 0, max_price: int = 0,
                        sort: str = 'PRICE_LOW_TO_HIGH') -> dict:
    """
    Ищет отели по множеству фильтров
    :param region_id: id региона полученный из get_locations_by_query()
    :param adults: количество путешественников
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
        response = requests.request("POST", url, json=payload, headers=headers, timeout=20)
    except requests.ConnectTimeout:
        raise ApiException(ApiException.timeout_error)

    if response.status_code == requests.codes.ok:
        response = json.loads(response.text)
        # #########################################################################################
        # with open('api_services/hotels/hotels.json', 'w') as file:
        #     file.write(json.dumps(response, indent=4, ensure_ascii=False))
        # #########################################################################################
        try:
            properties = response['data']['propertySearch']['properties']
            return properties
        except TypeError:
            raise ApiException(ApiException.no_result)
    else:
        raise ApiException(f'{ApiException.bad_request} код: {response.status_code}')


def _parse_hotel_id(properties: dict):
    hotel_id = properties['id']
    return hotel_id


def _parse_hotel_name(properties: dict):
    hotel_name = properties['name']
    return hotel_name


def _parse_destination(properties: dict):
    distance_from_center = properties['destinationInfo']['distanceFromDestination']['value']
    return distance_from_center


def _parse_price(properties: dict):
    price = properties['price']['lead']['formatted']
    return price


def _parse_reviews(properties: dict):
    reviews = properties['reviews']['score']
    return reviews

# _properties_request(region_id='6053839', num_of_results=10,
#                     check_in_date=date.today(), check_out_date=date.today() + timedelta(days=7))
