import logging
import utils
import settings
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
            if text[6] == settings.MAIL_PASSWORD:
                text[1] = URL.get_by_id(int(text[1])).url # Get URL string base on id in DB
                utils.addTask(*text[:6])
            else:
                logging.error("Password incorrect")
