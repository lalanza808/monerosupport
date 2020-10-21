import datetime
from peewee import *
import config


db = SqliteDatabase(config.SQLITE_DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db

class SupportRequest(BaseModel):
    reddit_user = CharField()
    solved = BooleanField(default=False)
    # todo...
