#!/usr/bin/env python

import webapp2
import urllib2
import logging
from bs4 import BeautifulSoup
import datetime

from google.appengine.ext import db


class SendTask(db.Model):
    telephone = db.StringProperty()
    url = db.StringProperty()
    periodLimit = db.IntegerProperty()
    sendDateTimeList = db.ListProperty(datetime.datetime)
    active = db.BooleanProperty()


class MainHandler(webapp2.RequestHandler):
    def get(self):
        url = "http://www.yr.no/place/France/Rh%C3%B4ne-Alpes/Saint-Genis-Pouilly/varsel.xml"
        soup = BeautifulSoup(urllib2.urlopen(url))
        logging.info(
            "Place: " + soup.weatherdata.location.contents[1].contents[0])
        for i, period in enumerate(soup.find_all('time')):
            logging.info("--------- Period: " + str(i))
            logging.info(
                "Time: " + period.get('from') + " - " + period.get('to'))
            logging.info("Weather: " + period.symbol.get('name'))
            logging.info(
                "Precipitation: " + period.precipitation.get('value') + "mm")
            logging.info("Wind: " + period.windspeed.get(
                'mps') + "m/s " + period.winddirection.get('code'))
            logging.info(
                "Temperature: " + period.temperature.get('value') + 'C')
            logging.info("Pressure: " + period.pressure.get('value') + 'hpa')
        self.response.write('ok')


class CheckCron(webapp2.RequestHandler):
    def get(self):
        logging.info("ok")


class AddTask(webapp2.RequestHandler):
    def post(self):
        sendTask = SendTask()

        sendTask.telephone = self.request.get('telephone')
        sendTask.url = self.request.get('url')
        sendTask.periodLimit = int(self.request.get('periods'))
        logging.info(self.request.get('sendDateTimeList').split('\n'))
        sendTask.sendDateTimeList = [datetime.datetime.strptime(dateString, '%d-%m-%Y %H:%M') for dateString in self.request.get('sendDateTimeList').split('\r\n')]
        sendTask.active = True

        sendTask.put()

        self.redirect('/list')


class TaskList(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')

        sendTasks = db.GqlQuery(
            "SELECT * FROM SendTask WHERE active = TRUE ORDER BY active DESC")
        self.response.out.write('<b>Active tasks:</b><br>')
        for task in sendTasks:
            self.response.out.write('telephone: %s, url: %s, periodLimit: %d, sendDateTimeList: %s, active: %d'
                                    % (task.telephone, task.url, task.periodLimit, task.sendDateTimeList, task.active))
            self.response.out.write('<br>')
        self.response.out.write('<br>')
        self.response.out.write('<b>New task:</b><br>')
        self.response.out.write("""
              <form action="/addTask" method="post">
                <div>Telephone: <input type="text" name="telephone" value="+48123456" ></input></div>
                <div>URL: <input type="text" name="url" value="http://www.onet.pl"></input></div>
                <div>Period limit: <input type="text" name="periods" value="3"></input></div>
                <div>Send DateTime List: <textarea name="sendDateTimeList" rows="10" cols="60">05-06-2012 10:22</textarea></div>
                <div><input type="submit" value="Add Task"></div>
              </form>
            </body>
          </html>""")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/list', TaskList),
    ('/addTask', AddTask),
    ('/check', CheckCron)
], debug=True)
