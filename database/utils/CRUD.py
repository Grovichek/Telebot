from datetime import datetime

from api_services.hotels.get_properties import HotelInfo
from config_data.config import HISTORY_SIZE
from database.common.models import User, UserHistory, HistoryContent, Image, db


def create_history_element(db: db, telegram_id: int, command: str, hotels: list[HotelInfo]) -> None:
    """
    Создаёт элемент истории для пользователя по его telegram id
    :param db: база данных
    :param telegram_id:
    :param command: тип сортировки выбранный пользователем
    :param hotels: список экземпляров HotelInfo
    :return: ничего
    """
    with db:
        _create_user(user_id=telegram_id)
        history_element = UserHistory.create(user=telegram_id,
                                             command=command,
                                             date=datetime.now().strftime("%m/%d/%Y, %H:%M"))
        _create_history_content(history_element=history_element, hotels=hotels)


def delete_last_history_element(db: db, telegram_id: int) -> None:
    """
    Удаляет самый старый элемент истории пользователя если размер истории превысил HISTORY_SIZE (задаётся в config.py)
    :param db: база данных
    :param telegram_id:
    :return: ничего
    """
    with db:
        user_history = get_history_elements(db, telegram_id)
        if len(user_history) > HISTORY_SIZE:
            for content_element in _get_history_content(user_history[0]):
                for image in _get_images_by_id(content_element):
                    Image[image].delete_instance()
                HistoryContent[content_element].delete_instance()
            UserHistory[user_history[0]].delete_instance()


def get_history_elements(db: db, telegram_id: int) -> list[UserHistory]:
    """
    :param db: база данных
    :param telegram_id:
    :return: список элементов истории пользователя
    """
    with db:
        list_of_history_elements = [uh for uh in UserHistory.select().where(UserHistory.user_id == telegram_id)]
        return list_of_history_elements


def get_history_content(db: db, history_element: str | UserHistory) -> list[HotelInfo]:
    """
    Получает из базы данных контент связанный с элементом истории history_element,
    создаёт список экземпляров HotelInfo
    :param db: база данных
    :param history_element: элемент истории (UserHistory или его id)
    :return: список экземпляров HotelInfo связанных с элементом истории history_element
    """
    with db:
        results = []
        for history_content_item in HistoryContent.select().where(HistoryContent.user_history_id == history_element):
            results.append(HotelInfo(
                hotel_id=history_content_item.hotel_id,
                hotel_name=history_content_item.hotel_name,
                distance_from_center=history_content_item.distance_from_center,
                price=history_content_item.price,
                reviews=history_content_item.reviews,
                address=history_content_item.address,
                star_rating=history_content_item.star_rating,
                images=[image.image_url for image in
                        Image.select().where(Image.history_content == history_content_item)]
            ))
    return results


def _create_user(user_id: int) -> None:
    """
    Создаёт пользователя в базе данных если его там небыло
    :param user_id: telegram id
    :return: ничего
    """
    if user_id not in User:
        User.create(telegram_id=user_id)


def _create_history_content(history_element: UserHistory, hotels: list[HotelInfo]) -> None:
    """
    Сохраняет в базе данных всю информацию из HotelInfo связанную с history_element
    :param history_element: элемент истории UserHistory
    :param hotels: список экземпляров HotelInfo
    :return: ничего
    """
    for hotel in hotels:
        history_content = HistoryContent.create(user_history=history_element,
                                                hotel_id=hotel.hotel_id,
                                                hotel_name=hotel.hotel_name,
                                                distance_from_center=hotel.distance_from_center,
                                                price=hotel.price,
                                                reviews=hotel.reviews,
                                                address=hotel.address,
                                                star_rating=hotel.star_rating)
        for image in hotel.images:
            Image.create(history_content=history_content, image_url=image)


def _get_history_content(history_element: UserHistory) -> list[HistoryContent]:
    """
    Получает из базы все элементы HistoryContent связанные с history_element
    :param history_element: элемент истории UserHistory
    :return: список из HistoryContent
    """
    history_content = [history_content_item for history_content_item in
                       HistoryContent.select().where(HistoryContent.user_history_id == history_element)]
    return history_content


def _get_images_by_id(history_content: HistoryContent) -> list[Image]:
    """
    Получает из базы все элементы Image связанные с history_content
    :param history_content:
    :return:
    """
    images = [image for image in Image.select().where(Image.history_content_id == history_content)]
    return images
