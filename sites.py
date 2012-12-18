import logging
import urllib2
from bs4 import BeautifulSoup


class WeatherSite(object):
    def __init__(self, url, periods):
        super(WeatherSite, self).__init__()
        self.url = url
        self.periods = periods
        self.xml = BeautifulSoup(urllib2.urlopen(url))
        self.periodPattern = '{start}-{end} {symbol} {precipitation}mm {wind}m/s {temp}C '

    def generateText(self):
        pass


class Yr(WeatherSite):
    def __init__(self, url, periods):
        super(Yr, self).__init__(url, periods)

    def generateText(self):
        text = self.xml.weatherdata.location.contents[1].contents[0] + ' '
        for i, period in enumerate(self.xml.find_all('time'), start=1):
            if i in self.periods:
                text += self.periodPattern.format(start=period.get('from')[8:13],
                                                  end=period.get('to')[11:13],
                                                  symbol=period.symbol.get('name'),
                                                  precipitation=period.precipitation.get('value'),
                                                  wind=period.windspeed.get('mps'),
                                                  temp=period.temperature.get('value'))
        return text.encode('latin-1')
