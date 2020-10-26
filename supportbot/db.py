from datetime import datetime
from peewee import *
from supportbot import config


db = SqliteDatabase(config.SQLITE_DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db

class IRCSupportOperator(BaseModel):
    irc_nick = CharField()
    is_a_regular = BooleanField()
    is_support_admin = BooleanField()

class SupportRequest(BaseModel):
    post_id = CharField()
    timestamp = DateTimeField(default=datetime.now)
    author = CharField()
    title = CharField()
    permalink = CharField()
    solved = BooleanField(default=False)
    assigned = BooleanField(default=False)
    assignee = ForeignKeyField(IRCSupportOperator, backref='assignee', null=True)

db.create_tables([SupportRequest, IRCSupportOperator])
