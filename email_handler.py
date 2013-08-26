import logging
import utils
import settings
from sms import GSMService
from model import URL
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler


class EmailHandler(InboundMailHandler):
    def receive(self, message):
        logging.info("Processing a message from: " + message.sender)
        plaintext_bodies = message.bodies('text/plain')
        for content_type, body in plaintext_bodies:
            text = body.decode()
            logging.info("Text: " + text)
            text = text.strip().split('#')
            #format: phone_number#url_id#periods#dates#sms_type#sms_sender#password
            if len(text) == 7 and text[6] == settings.MAIL_PASSWORD:
                logging.info('weather request...')
                text[1] = URL.get_by_id(int(text[1])).url #get URL string based on id in DB
                utils.addTask(*text[:6])
            #format: phone_number#text#password
            elif len(text) == 3 and text[2] == settings.MAIL_PASSWORD:
                logging.info('sms request...')
                gs = GSMService()
                gs.sendSMS(text[1], text[0], 'poland')
            else:
                logging.error("Password or format incorrect")
