import requests
from config_data import config
import json
import datetime
import random

BASE_URL_API = 'https://hotels4.p.rapidapi.com'


def get_locations(query: str, locale: str = 'ru_RU') -> dict | bool:
    """Поиск города/страны принимает строку, возвращает json с результатом"""

    url = f"{BASE_URL_API}/locations/v3/search"
    querystring = {"q": query, "locale": locale, "langid": "1033", "siteid": "300000001"}

    headers = {
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)

    if len(response['sr']) > 0:
        return response
    else:
        return False

# TODO что делает фукнкция ?
# TODO list set dcit tuple в коде не используем
def get_list(region_id: str,
             adults: int,
             results_size: int,
             sort: str,
             check_in_date: datetime = datetime.date.today(),
             check_out_date: datetime = datetime.date.today() + datetime.timedelta(days=7),
             min_price: int = 10,
             max_price: int = 150,
             locale: str = "ru_RU"):
    url = f"{BASE_URL_API}/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": locale,
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
        "resultsSize": results_size,
        "sort": sort,
        "filters": {"price": {
            "max": max_price,
            "min": min_price
        }}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return json.loads(response.text)


def get_photos(property_id: str, count: int, locale="ru_RU"):
    url = f"{BASE_URL_API}/properties/v2/get-summary"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": locale,
        "siteId": 300000001,
        "propertyId": property_id
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "5e42aa4f74mshc4de80ea651800ap1b2f7fjsn5d2f64a70ebc",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = json.loads(requests.request("POST", url, json=payload, headers=headers).text)

    result = []
    for photo in response["data"]["propertyInfo"]["propertyGallery"]["images"]:
        result.append((photo["image"]["url"], photo["image"]["description"]))

    return random.sample(result, count)


