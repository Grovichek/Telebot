from peewee import *
import os

db = SqliteDatabase(os.path.join('database', 'my_data.db'))


class DatabaseException(Exception):
    pass


class User(Model):
    user_id = PrimaryKeyField(null=False)
    fname = CharField(max_length=20)
    lname = CharField(max_length=20)
    age = IntegerField()
    country = CharField(max_length=20)
    city = CharField(max_length=20)
    phone = IntegerField()

    class Meta:
        database = db


def create_db() -> None:
    """Создаёт файл базы данных если он небыл создан ранее"""
    if not os.path.exists(os.path.join('database', 'my_data.db')):
        User.create_table()
    else:
        print('База данных уже была создана ранее')


def create_user_by_id(user_id, **kwargs) -> None:
    """Создаёт нового пользователя в базе данных, принимает id, далее запрос в виде key=value через запятую"""
    if user_id not in User:
        User.create(user_id=user_id, **kwargs)
    else:
        raise DatabaseException('Пользователь с таким id уже есть в базе')


def update_user_by_id(user_id, **kwargs) -> None:
    """Перезаписывает данные существующего пользователя принимает id, далее запрос в виде key=value через запятую"""
    if user_id in User:
        for i in kwargs.items():
            User.update({i[0]: i[1]}).where(User.user_id == user_id).execute()
    else:
        raise DatabaseException('Пользователя с таким id не существует в базе')
