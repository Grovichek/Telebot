import random
import asyncio
from aiohttp import ClientSession
import aiofiles

from api_services.hotels.get_properties import HotelInfo
from config_data.config import HOTELS_API_URL, RAPID_API_KEY
from exceptions import ApiException


async def get_hotels_detail(hotels: list[HotelInfo], num_of_images: int) -> list[HotelInfo]:
    """
    :param hotels: список экземпляров HotelInfo
    :param num_of_images: необходимое количество фотографий
    :return: список обновлённых экземпляров HotelInfo
    """
    tasks = []
    for hotel in hotels:
        await asyncio.sleep(.25)  # API принимает не больше 5 запросов в сек

        tasks.append(asyncio.create_task(_update_hotel(hotel=hotel,
                                                       detail=await _detail_request(hotel_id=hotel.hotel_id),
                                                       num_of_images=num_of_images)))

    results = await asyncio.gather(*tasks)
    # TODO Не понятно почему светится ретёрн, типы совпадают
    return results


async def _update_hotel(hotel: HotelInfo, detail: dict, num_of_images: int):
    hotel = hotel._replace(
        images=await _parse_hotel_images(detail=detail, num_of_images=num_of_images),
        address=await _parse_hotel_address(detail=detail),
        star_rating=await _parse_star_rating(detail=detail)
    )
    return hotel


async def _detail_request(hotel_id: str):
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
            "locale": "en_US",
            "siteId": 300000001,
            "propertyId": f"{hotel_id}"
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }
        try:
            async with session.request(method="POST",
                                       url=url,
                                       json=payload,
                                       headers=headers,
                                       params=payload,
                                       timeout=15) as response:

                return await response.json()
        except:
            raise ApiException('Не удалось связаться с сервером')


# def _detail_request(property_id: str) -> dict: # Синхронный запрос
#     """
#     Запрос к API
#     :param property_id: id отеля
#     :return: ответ сервера
#     """
#     url = f"{HOTELS_API_URL}/properties/v2/detail"
#
#     payload = {
#         "currency": "USD",
#         "eapid": 1,
#         "locale": "ru_RU",
#         "siteId": 300000001,
#         "propertyId": f"{property_id}"
#     }
#
#     headers = {
#         "content-type": "application/json",
#         "X-RapidAPI-Key": RAPID_API_KEY,
#         "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
#     }
#
#     try:
#         response = requests.request("POST", url, json=payload, headers=headers, timeout=20)
#     except:
#         raise ApiException('Время истекло')
#
#     if response.status_code == requests.codes.ok:
#         response = json.loads(response.text)
#         # with open('detail.json', 'w') as file:
#         #     file.write(json.dumps(response, indent=4, ensure_ascii=False))
#         return response
#     else:
#         raise ApiException(f'Неправильный запрос. код: {response.status_code}')


async def _parse_hotel_images(detail: dict, num_of_images: int) -> list:
    """
    :param detail: словарь с сервера
    :param num_of_images: необходимое количество фотографий
    :return: список из num_of_images СЛУЧАЙНЫХ url-ов или все имеющиеся url
    """
    result = list()
    for image in detail['data']['propertyInfo']['propertyGallery']['images']:
        result.append(image['image']['url'])
    if num_of_images <= len(result):
        return random.sample(result, num_of_images)
    else:
        return random.sample(result, len(result))


async def _parse_hotel_address(detail: dict) -> str:
    """
    получение адреса отеля
    :param detail: словарь с сервера
    :return: адрес отеля
    """
    try:
        address = detail['data']['propertyInfo']['summary']['location']['address']['addressLine']
    except:
        address = 'Не известно'
    return address


async def _parse_star_rating(detail: dict) -> str:
    """
    Получение количества звёзд отеля
    :param detail: словарь с сервера
    :return: количества звёзд отеля
    """
    try:
        star_rating = detail['data']['propertyInfo']['summary']['overview']['propertyRating']['rating']
    except:
        star_rating = 'Не известно'
    return star_rating
