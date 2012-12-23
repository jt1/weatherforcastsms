#!/usr/bin/env python

import webapp2
import logging
import datetime
from google.appengine.ext import db
from model import Task
from sms import GSMPortal
from sites import Yr, Meteoblue


class SendSMS(webapp2.RequestHandler):
    def __init__(self, request, response):
        self.initialize(request, response)
        self.sites = {"yr": Yr, "meteoblue": Meteoblue}
        self.smsSender = GSMPortal()

    def get(self):
        for task in db.GqlQuery("SELECT * FROM Task WHERE sendDateTimeList != NULL"):
            sendDateTimeToDelete = list()
            for sendDateTime in task.sendDateTimeList:
                if sendDateTime < datetime.datetime.now() + datetime.timedelta(hours=1):
                    for siteCand in self.sites:
                        if siteCand in task.url:
                            site = self.sites[siteCand](task.url, task.periods)
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
        task = Task(phone=self.request.get('phone').strip(),
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
            self.response.out.write('phone: {}, periods: {}, sendDateTimeList: {}, url: {}<br>'.format(task.phone, task.periods, task.sendDateTimeList, task.url))
        self.response.out.write("""
            <form action="/addTask" method="post">
                <div><input type="button" value="Send now" onclick="location.href='/send';"></div>
                <br><b>New task:</b><br>
                <div>url: <input type="text" name="url" size="80" value="http://www.yr.no/place/France/Rh%C3%B4ne-Alpes/Chamonix/varsel.xml"></input></div>
                <div>phone: <input type="text" name="phone" value="48123456" ></input></div>
                <div>periods: <input type="text" name="periods" value="0;1;2;3"></input></div>
                <div>send date/time list (use ';' as a separator):</div>
                <div><textarea name="sendDateTimeList" rows="10" cols="65">""" + (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%d-%m-%Y %H:%M") + """</textarea></div>
                <div><input type="submit" value="Add task"></div>
              </form>
            </body>
          </html>""")


app = webapp2.WSGIApplication([
    ('/', TaskList),
    ('/send', SendSMS),
    ('/addTask', AddTask)])
