from google.appengine.ext import db
import datetime


class Task(db.Model):
    site = db.StringProperty()
    phone = db.StringProperty()
    url = db.StringProperty()
    periods = db.ListProperty(int)
    sendDateTimeList = db.ListProperty(datetime.datetime)
