import os
from datetime import datetime
from peewee import *

from api_services.hotels.get_properties import HotelInfo
from config_data.config import HISTORY_SIZE

# TODO Раскидать модели по модулям
db = SqliteDatabase(os.path.join("database", "data.db"))


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    telegram_id = PrimaryKeyField()

    @staticmethod
    def create_user(telegram_id):
        if telegram_id not in User:
            return User.create(telegram_id=telegram_id)
        else:
            return User.get(User.telegram_id == telegram_id)


class UserHistory(BaseModel):
    user = ForeignKeyField(User)
    command = TextField()
    date = DateTimeField()

    @staticmethod
    def create_history_element(user, command):
        return UserHistory.create(user=user,
                                  command=command,
                                  date=datetime.now().strftime("%m/%d/%Y, %H:%M"))

    @staticmethod
    def get_list_of_history_elements(user):
        return [user_history for user_history in UserHistory.select().where(UserHistory.user_id == user)]

    @staticmethod
    def delete_history_element(user):
        user_history = UserHistory.get_list_of_history_elements(user)
        if len(user_history) > HISTORY_SIZE:
            for content_item in HistoryContent.get_history_content(user_history[0]):
                for image in Image.get_images_list_by_id(content_item):
                    Image[image].delete_instance()
                HistoryContent[content_item].delete_instance()
            UserHistory[user_history[0]].delete_instance()


class HistoryContent(BaseModel):
    user_history = ForeignKeyField(UserHistory)
    hotel_id = TextField()
    hotel_name = TextField()
    distance_from_center = FloatField()
    price = TextField()
    reviews = FloatField()
    address = TextField()
    star_rating = FloatField()

    @staticmethod
    def create_history_content(history_item, hotels):
        for hotel in hotels:
            history_content = HistoryContent.create(user_history=history_item,
                                                    hotel_id=hotel.hotel_id,
                                                    hotel_name=hotel.hotel_name,
                                                    distance_from_center=hotel.distance_from_center,
                                                    price=hotel.price,
                                                    reviews=hotel.reviews,
                                                    address=hotel.address,
                                                    star_rating=hotel.star_rating)
            for image in hotel.images:
                Image.create(history_content=history_content, image_url=image)

    @staticmethod
    def get_history_content(history_item):
        return [history_content_item for history_content_item in
                HistoryContent.select().where(HistoryContent.user_history_id == history_item)]

    @staticmethod
    def get_list_of_history_content(history_item):
        results = []
        for history_content_item in HistoryContent.select().where(HistoryContent.user_history_id == history_item):
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


class Image(BaseModel):
    history_content = ForeignKeyField(HistoryContent)
    image_url = TextField()

    @staticmethod
    def get_images_list_by_id(content_id):
        return [image for image in Image.select().where(Image.history_content_id == content_id)]


def create_tables():
    with db:
        db.create_tables([User, UserHistory, HistoryContent, Image])
