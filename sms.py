import settings
import urllib
import logging
from google.appengine.api import urlfetch


class SenderSMS(object):
    def __init__(self):
        super(SenderSMS, self).__init__()
        self.smsTypes = {'poland': '3', 'other': '1'}

    def sendSMS(self, text, phone, smsType):
        pass


class GSMService(SenderSMS):
    def __init__(self):
        super(GSMService, self).__init__()

    def sendSMS(self, text, phone, smsType):
        params = {
            "login": settings.GSMSERVICE_LOGIN,
            "pass": settings.GSMSERVICE_PASSWORD,
            "text": text.encode('ascii', 'replace'),
            "recipient": phone,
            "type": self.smsTypes[smsType],
        }
        payload = urllib.urlencode(params)
        result = urlfetch.fetch(url=settings.GSMSERVICE_SMS_URL,
                                payload=payload,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        logging.info("Result code: {}, content: {}".format(result.status_code, result.content))
        return result.status_code == 200 and result.content.startswith("003")
