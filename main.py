#!/usr/bin/env python

import webapp2
import logging
import datetime
from google.appengine.ext import db
from model import Task
from sites import Yr
from sms import GSMPortal


class SendSMS(webapp2.RequestHandler):
    def __init__(self, request, response):
        self.initialize(request, response)
        self.sites = {"yr": Yr}
        self.smsSender = GSMPortal()

    def get(self):

        for task in db.GqlQuery("SELECT * FROM Task WHERE sendDateTimeList != NULL"):
            sendDateTimeToDelete = list()
            for sendDateTime in task.sendDateTimeList:
                if sendDateTime < datetime.datetime.now() + datetime.timedelta(hours=1):
                    site = self.sites[task.site](task.url, task.periods)
                    if self._sendSMS(self.smsSender, site, task.phone):
                        sendDateTimeToDelete.append(sendDateTime)
            task.sendDateTimeList = filter(lambda x: x not in sendDateTimeToDelete, task.sendDateTimeList)
            task.put()

    def _sendSMS(self, smsSender, site, phone):
        text = site.generateText()
        actionInfo = 'sending SMS to: {}, {} characters, text: {}'.format(phone, len(text), text)
        logging.info(actionInfo)
        self.response.write(actionInfo + '<br>')
        if smsSender.sendSMS(text, phone):
            logging.info('SMS sent')
            self.response.write('SMS sent<br>')
            return True
        logging.info('SMS failed')
        self.response.write('SMS failed<br>')
        return False


class AddTask(webapp2.RequestHandler):
    def post(self):
        task = Task(site=self.request.get('site').strip(),
                    phone=self.request.get('phone').strip(),
                    url=self.request.get('url').strip(),
                    periods=map(
                    int, self.request.get('periods').split(';')),
                    sendDateTimeList=[datetime.datetime.strptime(dateString.strip(), '%d-%m-%Y %H:%M') for dateString in self.request.get('sendDateTimeList').split(';')])
        task.put()
        self.redirect('/')


class TaskList(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body><b>All tasks:</b><br>')
        for task in db.GqlQuery("SELECT * FROM Task"):
            self.response.out.write('site: {}, phone: {}, periods: {}, sendDateTimeList: {}, url: {}<br>'.format(task.site, task.phone, task.periods, task.sendDateTimeList, task.url))
        self.response.out.write("""<br><b>New task:</b><br>
              <form action="/addTask" method="post">
                <div>site:
                    <input type="radio" name="site" value="yr" checked>yr.no
                    <input type="radio" name="site" value="meteoblue">meteoblue.com
                </div>
                <div>url: <input type="text" name="url" size="80" value="http://www.yr.no/place/France/Rh%C3%B4ne-Alpes/Chamonix/varsel.xml"></input></div>
                <div>phone: <input type="text" name="phone" value="48123456" ></input></div>
                <div>periods: <input type="text" name="periods" value="1;2;3"></input></div>
                <div>send date/time list:</div>
                <div><textarea name="sendDateTimeList" rows="10" cols="65">""" + (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%d-%m-%Y %H:%M") + """</textarea></div>
                <div><input type="submit" value="Add task"> <input type="button" value="Send now" onclick="location.href='/send';"></div>
              </form>
            </body>
          </html>""")


app = webapp2.WSGIApplication([
    ('/', TaskList),
    ('/send', SendSMS),
    ('/addTask', AddTask)])
