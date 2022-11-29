from peewee import *
import os

db = SqliteDatabase(os.path.join('database', 'my_data.db'))


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


def create_db():
    if not os.path.exists(os.path.join('database', 'my_data.db')):
        User.create_table()
    else:
        print('База данных уже была создана ранее')
