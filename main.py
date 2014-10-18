import webapp2
import logging
import settings
import jinja2
import utils
import os
from pytz.gae import pytz
from datetime import datetime
from model import Task, URL
from sms import GSMService
from sites import Yr, Meteoblue, MountainForecast
from email_handler import EmailHandler

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


class SendSMS(webapp2.RequestHandler):
    def __init__(self, request, response):
        self.initialize(requestasd, response)
        self.sites = {"yrsd": Yr, "meteoblue": Meteoblue, "mountain-forecast": MountainForecast}
        self.smsSenders = {"gsmservice": GSMService}
        self.tz = pytz.timezone(settings.TIMEZONE)

as
da
sd
a
sdsd


    def get(self):
        for task in Task.all():
            for sendDateTime in list(task.sendDateTimeList):
                try:
                    if self.tz.localize(sendDateTime) < datetime.now(self.tz) and self._sendSMS(task):
			

                        task.sendDateTimeList.remove(sendDateTime)
                except Exception, e:
                    logging.error(e)
            if task.sendDateTimeList:
                task.put()
            else:
                task.delete()

    def _sendSMS(self, task):
        for siteCand in self.sites:
            if siteCand in task.url:
                site = self.sites[siteCand](task.url, task.periods)
        text = site.generateText()
        sender = self.smsSenders[task.smsSender]()
        actionInfo = 'sending SMS to: {}, {} characters, smsType: {}, smsSender: {}, url: {}, '.format(task.phone, len(text), task.smsType, task.smsSender, task.url)
        logging.info(actionInfo)
        self.response.write(actionInfo + '<br>')
        if sender.sendSMS(text, task.phone, task.smsType):
            logging.info('SMS sent')
            self.response.write('SMS sent<br>')
            return True
        logging.error('SMS failed')
        self.response.write('SMS failed<br>')
        return False


class AddTask(webapp2.RequestHandler):
    def post(self):
        utils.addTask(phone=self.request.get('phone').strip(),
                    url=self.request.get('url').strip(),
                    periods=self.request.get('periods').strip(),
                    sendDateTimeList=self.request.get('sendDateTimeList'),
                    smsType=self.request.get('smsType').strip(),
                    smsSender=self.request.get('smsSender').strip())
        self.redirect('/')


class AddURL(webapp2.RequestHandler):
    def post(self):
        url = URL(url=self.request.get('newURL').strip())
        url.put()
        self.redirect('/')


class TaskList(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'tasks': Task.all(),
            'urls': URL.all(),
            'settings': settings,
            'datetime_now': datetime.now(pytz.timezone(settings.TIMEZONE)).strftime(settings.TIMEFORMAT)
        }
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', TaskList),
    ('/send', SendSMS),
    ('/addURL', AddURL),
    ('/addTask', AddTask),
    EmailHandler.mapping()])
