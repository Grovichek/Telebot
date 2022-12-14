import json
import aiofiles

import random
import asyncio
from aiohttp import ClientSession

from api_services.hotels.get_properties import HotelInfo
from config_data.config import HOTELS_API_URL, RAPID_API_KEY
from exceptions import ApiException


async def get_hotels_detail(hotels: list[HotelInfo], num_of_images: int) -> list[HotelInfo]:  # TODO Разобраться
    """
    Класс HotelInfo создаётся в модуле get_properties.py, тут он дополняется
    :param hotels: список экземпляров HotelInfo
    :param num_of_images: необходимое количество фотографий
    :return: список обновлённых экземпляров HotelInfo
    """
    tasks = []
    for hotel in hotels:
        await asyncio.sleep(0.25)  # API принимает не больше 5 запросов в сек
        tasks.append(asyncio.create_task(_update_hotel(property_info=await _detail_request(hotel_id=hotel.hotel_id),
                                                       num_of_images=num_of_images, hotel=hotel)))
    results = await asyncio.gather(*tasks)
    return results


async def _detail_request(hotel_id: str) -> dict:
    """
    запрос на сервер
    :param hotel_id: Экземпляр HotelInfo
    :return: обновлённый Экземпляр HotelInfo
    """
    async with ClientSession() as session:
        url = f"{HOTELS_API_URL}/properties/v2/detail"

        payload = {
            "currency": "USD",
            "eapid": 1,
            "locale": "ru_RU",
            "siteId": 300000001,
            "propertyId": f"{hotel_id}"
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }
        try:
            async with session.request(method="POST", url=url, json=payload, headers=headers,
                                       params=payload, timeout=20) as response:
                # ########################################################################################
                # async with aiofiles.open('api_services/hotels/detail.json', 'w') as file:
                #     text = await response.text()
                #     await file.write(json.dumps(json.loads(text), indent=4, ensure_ascii=False))
                # ########################################################################################
                if response.ok:
                    response = await response.json()
                    try:
                        property_info = response['data']['propertyInfo']
                        return property_info
                    except TypeError:
                        raise ApiException(ApiException.bad_request)
        except asyncio.TimeoutError:
            raise ApiException(ApiException.timeout_error)


async def _update_hotel(property_info: dict, num_of_images: int, hotel: HotelInfo):
    """
    :param property_info: json с сервера
    :param num_of_images: необходимое количество фотографий
    :param hotel: экземпляр HotelInfo
    :return: обновлённый экземпляр HotelInfo
    """
    hotel = hotel._replace(
        images=await _parse_hotel_images(property_info=property_info, num_of_images=num_of_images),
        address=await _parse_hotel_address(property_info=property_info),
        star_rating=await _parse_star_rating(property_info=property_info)
    )
    return hotel


async def _parse_hotel_images(property_info: dict, num_of_images: int) -> list:
    """
    :param property_info: json с сервера
    :param num_of_images: необходимое количество фотографий
    :return: список из num_of_images СЛУЧАЙНЫХ url-ов или все имеющиеся url
    """
    result = list()
    for image in property_info['propertyGallery']['images']:
        result.append(image['image']['url'])
    if num_of_images <= len(result):
        return random.sample(result, num_of_images)
    else:
        return random.sample(result, len(result))


async def _parse_hotel_address(property_info: dict) -> str:
    """
    :param property_info: словарь с сервера
    :return: адрес отеля
    """

    address = property_info['summary']['location']['address']['addressLine']

    return address


async def _parse_star_rating(property_info: dict) -> str:
    """
    :param property_info: словарь с сервера
    :return: количества звёзд отеля
    """
    try:
        star_rating = property_info['summary']['overview']['propertyRating']['rating']
    except TypeError:
        star_rating = 'Отсутствует'
    return star_rating
