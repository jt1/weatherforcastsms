import settings
import urllib
import logging
from google.appengine.api import urlfetch


class SenderSMS(object):
    def __init__(self):
        super(SenderSMS, self).__init__()

    def sendSMS(self, text, phone):
        pass


class GSMPortal(SenderSMS):
    def __init__(self):
        super(GSMPortal, self).__init__()

    def sendSMS(self, text, phone):
        params = {
            "login": settings.GSMSERVICE_LOGIN,
            "pass": settings.GSMSERVICE_PASSWORD,
            "text": text,
            "recipient": phone,
            "type": settings.GSMSERVICE_SMS_TYPE
        }
        payload = urllib.urlencode(params)
        result = urlfetch.fetch(url=settings.GSMSERVICE_SMS_URL,
                                payload=payload,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        logging.info("Result code: {0}, content: {1}".format(result.status_code, result.content))
        return result.status_code == 200 and result.content.startswith("003")
