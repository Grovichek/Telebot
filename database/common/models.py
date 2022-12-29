import os
from peewee import *

db = SqliteDatabase(os.path.join("database", "data.db"))


class BaseModel(Model):
    class Meta:
        database = db


# Иерархия в базе данных - User->UserHistory->HistoryContent->Image
class User(BaseModel):
    """
    Хранит telegram id пользователя
    """
    telegram_id = PrimaryKeyField()


class UserHistory(BaseModel):
    """
    Хранит экземпляр истории пользователя User
    """
    user = ForeignKeyField(User)
    command = TextField()
    date = DateTimeField()


class HistoryContent(BaseModel):
    """
    Хранит контент экземпляра истории UserHistory
    """
    user_history = ForeignKeyField(UserHistory)
    hotel_id = TextField()
    hotel_name = TextField()
    distance_from_center = FloatField()
    price = TextField()
    reviews = FloatField()
    address = TextField()
    star_rating = FloatField()


class Image(BaseModel):
    """
    Хранит ссылки на изображения для HistoryContent
    """
    history_content = ForeignKeyField(HistoryContent)
    image_url = TextField()
