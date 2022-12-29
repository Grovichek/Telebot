import os
from peewee import *

db = SqliteDatabase(os.path.join("database", "data.db"))


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    telegram_id = PrimaryKeyField()


class UserHistory(BaseModel):
    user = ForeignKeyField(User)
    command = TextField()
    date = DateTimeField()


class HistoryContent(BaseModel):
    user_history = ForeignKeyField(UserHistory)
    hotel_id = TextField()
    hotel_name = TextField()
    distance_from_center = FloatField()
    price = TextField()
    reviews = FloatField()
    address = TextField()
    star_rating = FloatField()


class Image(BaseModel):
    history_content = ForeignKeyField(HistoryContent)
    image_url = TextField()
