from google.appengine.ext import db
from datetime import datetime


class Task(db.Model):
    phone = db.StringProperty()
    url = db.StringProperty()
    periods = db.ListProperty(int)
    sendDateTimeList = db.ListProperty(datetime)
    smsType = db.StringProperty()
    smsSender = db.StringProperty()

class URL(db.Model):
    url = db.StringProperty()
