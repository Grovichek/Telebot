import json
import random
from telebot.types import InputMediaPhoto

import requests

from config_data.config import HOTELS_API_URL, RAPID_API_KEY
from exceptions import ApiException


def get_hotel_images(hotel_id: str, count: int) -> list[InputMediaPhoto]:
    detail = _detail_request(property_id=hotel_id)
    images = _parse_hotel_images(detail=detail, count=count)
    return images


def _detail_request(property_id: str) -> dict:
    """
    Запрос к API
    :param property_id: id отеля полученный из функции get_a_list_of_hotels_by_region_id()
    :return: Список кортежей содержащих ссылку на фото и описание фото
    """
    url = f"{HOTELS_API_URL}/properties/v2/detail"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "propertyId": property_id
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
        # with open('detail.json', 'w') as file:
        #     file.write(json.dumps(response, indent=4, ensure_ascii=False))
        return response
    else:
        raise ApiException(f'Неправильный запрос. код: {response.status_code}')


def _parse_hotel_images(detail: dict, count: int) -> list:
    result = list()
    for image in detail['data']['propertyInfo']['propertyGallery']['images']:
        result.append(InputMediaPhoto(media=image['image']['url'], caption=image['image']['description']))

    return random.sample(result, count)


# print(get_hotel_images('2528760', 5))
