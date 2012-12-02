#!/usr/bin/env python

import webapp2
import urllib
import urllib2
import logging
import datetime
import settings
from bs4 import BeautifulSoup
from google.appengine.api import urlfetch
from google.appengine.ext import db
from model import Task


class SendSMS(webapp2.RequestHandler):
    def get(self):
        for task in db.GqlQuery("SELECT * FROM Task WHERE sendDateTimeList != NULL"):
            sendDateTimeToDelete = list()
            for sendDateTime in task.sendDateTimeList:
                if sendDateTime < datetime.datetime.now() + datetime.timedelta(hours=1):
                    if self._sendSMS(self._getSMSText(task.url, task.periods), task.phone):
                        sendDateTimeToDelete.append(sendDateTime)
                        self.response.write('SMS sent<br>')
            task.sendDateTimeList = filter(lambda x: x not in sendDateTimeToDelete, task.sendDateTimeList)
            task.put()

    def _getSMSText(self, url, userPeriods):
        xml = BeautifulSoup(urllib2.urlopen(url))
        text = xml.weatherdata.location.contents[1].contents[0] + ' '
        for i, period in enumerate(xml.find_all('time'), start=1):
            if i in userPeriods:
                text += '{start}-{end} {symbol} {precipitation}mm {wind}m/s {temp}C '.format(start=period.get('from')[8:13], end=period.get('to')[11:13], symbol=period.symbol.get('name'), precipitation=period.precipitation.get('value'), wind=period.windspeed.get('mps'), temp=period.temperature.get('value'))
        return text.encode('latin-1')

    def _sendSMS(self, text, phone):
        logging.info('sending SMS to: {0}, {1} characters, text: {2}'.format(
            phone, len(text), text))
        params = {
            "login": settings.LOGIN,
            "pass": settings.PASSWORD,
            "text": text,
            "recipient": phone,
            "type": settings.SMS_TYPE
        }
        params = urllib.urlencode(params)
        result = urlfetch.fetch(url=settings.SMS_URL,
                                payload=params,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        logging.info("Result code: {0}, content: {1}".format(result.status_code, result.content))
        if result.status_code == 200 and result.content.startswith("003"):
            logging.info('SMS sent')
            return True
        logging.info('SMS failed')
        return False


class AddTask(webapp2.RequestHandler):
    def post(self):
        task = Task(phone=self.request.get('phone'),
                    url=self.request.get('url'),
                    periods=map(
                    int, self.request.get('periods').split(';')),
                    sendDateTimeList=[datetime.datetime.strptime(dateString, '%d-%m-%Y %H:%M') for dateString in self.request.get('sendDateTimeList').split(';')])
        task.put()
        self.redirect('/')


class TaskList(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body><b>All tasks:</b><br>')
        for task in db.GqlQuery("SELECT * FROM Task"):
            self.response.out.write('phone: {0}, periods: {1}, sendDateTimeList: {2}, url: {3}<br>'.format(task.phone, task.periods, task.sendDateTimeList, task.url))
        self.response.out.write("""<br><b>New task:</b><br>
              <form action="/addTask" method="post">
                <div>url: <input type="text" name="url" size="80" value="http://www.yr.no/place/France/Rh%C3%B4ne-Alpes/Chamonix/varsel.xml"></input></div>
                <div>phone: <input type="text" name="phone" value="48123456" ></input></div>
                <div>periods: <input type="text" name="periods" value="1;2;3"></input></div>
                <div>send date/time list:</div>
                <div><textarea name="sendDateTimeList" rows="10" cols="65">""" + (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%d-%m-%Y %H:%M") + """</textarea></div>
                <div><input type="submit" value="Add task"></div>
              </form>
            </body>
          </html>""")


app = webapp2.WSGIApplication([
    ('/', TaskList),
    ('/send', SendSMS),
    ('/addTask', AddTask)])
