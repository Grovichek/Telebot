from peewee import *
import os
from exceptions import DatabaseException

db_users = SqliteDatabase(os.path.join('database', 'users.db'))
db_history = SqliteDatabase(os.path.join('database', 'history.db'))


class User(Model):
    user_id = PrimaryKeyField(null=False)

    class Meta:
        database = db_users


class History(Model):
    user_id = ForeignKeyField(User, related_name='history')
    sort_type = CharField()
    city = CharField(max_length=20)
    check_in = DateField()
    check_out = DateField()
    is_show_images = BooleanField()

    class Meta:
        database = db_history


def create_empty_history_instance(user_id):
    return History.create(user_id=user_id, sort_type='None', city='None', check_in='None', check_out='None',
                          is_show_images=False)


def create_db_users() -> None:
    """Создаёт файл базы данных 'users.db' если он небыл создан ранее"""
    if not os.path.exists(os.path.join('database', 'users.db')):
        User.create_table()


def create_db_history() -> None:
    """Создаёт файл базы данных 'history.db' если он небыл создан ранее"""
    if not os.path.exists(os.path.join('database', 'history.db')):
        History.create_table()
