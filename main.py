#!/usr/bin/env python

import webapp2
import urllib2
import logging
from bs4 import BeautifulSoup


class MainHandler(webapp2.RequestHandler):
    def get(self):
        url = "http://www.yr.no/place/France/Rh%C3%B4ne-Alpes/Saint-Genis-Pouilly/varsel.xml"
        soup = BeautifulSoup(urllib2.urlopen(url))
        logging.info("Place: " + soup.weatherdata.location.contents[1].contents[0])
        for i, period in enumerate(soup.find_all('time')):
            logging.info("--------- Period: " + str(i))
            logging.info("Time: " + period.get('from') + " - " + period.get('to'))
            logging.info("Weather: " + period.symbol.get('name'))
            logging.info("Precipitation: " + period.precipitation.get('value') + "mm")
            logging.info("Wind: " + period.windspeed.get('mps') + "m/s " + period.winddirection.get('code'))
            logging.info("Temperature: " + period.temperature.get('value') + 'C')
            logging.info("Pressure: " + period.pressure.get('value') + 'hpa')

        self.response.write('ok')

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
