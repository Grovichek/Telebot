from database.common.models import *

db.connect()
db.create_tables([User, UserHistory, HistoryContent, Image])
