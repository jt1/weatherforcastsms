import webapp2
import logging
import settings
from pytz.gae import pytz
from datetime import datetime
from model import Task, URL
from sms import GSMService
from sites import Yr, Meteoblue, MountainForecast


class SendSMS(webapp2.RequestHandler):
    def __init__(self, request, response):
        self.initialize(request, response)
        self.sites = {"yr": Yr, "meteoblue": Meteoblue, "mountain-forecast": MountainForecast}
        self.smsSenders = {"gsmservice": GSMService}
        self.tz = pytz.timezone(settings.TIMEZONE)

    def get(self):
        for task in Task.all():
            sendDateTimeToDelete = list()
            for sendDateTime in task.sendDateTimeList:
                try:
                    if self.tz.localize(sendDateTime) < datetime.now(self.tz) and self._sendSMS(task):
                        sendDateTimeToDelete.append(sendDateTime)
                except Exception, e:
                    logging.error(e)
            task.sendDateTimeList = filter(lambda x: x not in sendDateTimeToDelete, task.sendDateTimeList)
            task.put()

    def _sendSMS(self, task):
        for siteCand in self.sites:
            if siteCand in task.url:
                site = self.sites[siteCand](task.url, task.periods)
        text = site.generateText().encode('latin-1')
        sender = self.smsSenders[task.smsSender]()
        actionInfo = 'sending SMS to: {}, {} characters, smsType: {}, smsSender: {}, text: {}, '.format(task.phone, len(text), task.smsType, task.smsSender, text)
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
        task = Task(phone=self.request.get('phone').strip(),
                    url=self.request.get('url').strip(),
                    periods=map(
                    int, self.request.get('periods').strip().split(';')),
                    sendDateTimeList=[datetime.strptime(dateString.strip(), settings.TIMEFORMAT) for dateString in self.request.get('sendDateTimeList').split(';') if dateString.strip()],
                    smsType=self.request.get('smsType').strip(),
                    smsSender=self.request.get('smsSender').strip())
        task.put()
        self.redirect('/')


class AddURL(webapp2.RequestHandler):
    def post(self):
        url = URL(url=self.request.get('newURL').strip())
        url.put()
        self.redirect('/')


class TaskList(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body><b>All tasks:</b><br>')
        for task in Task.all():
            self.response.out.write('phone: {}, periods: {}, sendDateTimeList: {}, url: {}, smsType: {}, smsSender: {}<br>'.format(task.phone, task.periods, task.sendDateTimeList, task.url, task.smsType, task.smsSender))
        self.response.out.write('''
            <form action="/addURL" method="post">
                <br><b>New URL:</b><br>
                <div>URL (yr, meteoblue, mountain-forecast): <input type="text" name="newURL" size="80"></input><input type="submit" value="Add URL">
            </form>
            <form action="/addTask" method="post">
                <br><b>New task:</b><br>
                <div>sms sender:
                    <select name="smsSender">
                        <option value="gsmservice">GSMService.pl</option>
                    </select>
                </div>
                <div>select URL:
                    <select name="url">''')
        for url in URL.all():
            self.response.out.write('<option>%s</option>' % url.url)
        self.response.out.write('''
                    </select>
                </div>            
                <div>phone: <input type="text" name="phone" value="''' + settings.PHONE_DEFAULT + '''" ></input></div>
                <div>sms type:
                    <select name="smsType">
                        <option value="poland">Poland</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div>periods: <input type="text" name="periods" value="0;1;2;3"></input></div>
                <div>send date/time list (use ';' as a separator):</div>
                <div><textarea name="sendDateTimeList" rows="10" cols="65">''' + datetime.now(pytz.timezone(settings.TIMEZONE)).strftime(settings.TIMEFORMAT) + ''';</textarea></div>
                <div>
                    <input type="submit" value="Add task">
                    <input type="button" value="Send now" onclick="location.href='/send';">
                </div>
              </form>
            </body>
          </html>''')


app = webapp2.WSGIApplication([
    ('/', TaskList),
    ('/send', SendSMS),
    ('/addURL', AddURL),
    ('/addTask', AddTask)])
