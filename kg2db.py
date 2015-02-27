import os
from peewee import *

DIR = os.path.dirname(os.path.realpath(__file__))
database = SqliteDatabase("{}/already_done.sqlite".format( DIR ), **{})

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class AlreadyDone(BaseModel):
    id = PrimaryKeyField(db_column='ID')
    commentid = CharField(db_column='commentid')

    class Meta:
        db_table = 'already_done'

def get_comment(commentID):
    for i in AlreadyDone.select(AlreadyDone.commentid).where(AlreadyDone.commentid == commentID):
        return i
    return None

def add_comment(commentID):

    return AlreadyDone.create(
        commentid=commentID
    )

AlreadyDone.create_table(True)
