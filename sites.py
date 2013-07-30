import urllib2
from bs4 import BeautifulSoup


class WeatherSite(object):
    def __init__(self, url, periods):
        super(WeatherSite, self).__init__()
        self.periods = periods

    def generateText(self):
        pass


class Yr(WeatherSite):
    def __init__(self, url, periods):
        super(Yr, self).__init__(url, periods)
        self.xml = BeautifulSoup(urllib2.urlopen(url))
        self.periodPattern = '{start}-{end} {symbol} {precipitation}mm {wind}m/s {temp}C '

    def generateText(self):
        text = self.xml.weatherdata.location.contents[1].contents[0] + ' '
        dataPeriods = self.xml.find_all('time')
        for i in self.periods:
            text += self.periodPattern.format(start=dataPeriods[i].get('from')[8:13],
                                              end=dataPeriods[i].get('to')[11:13],
                                              symbol=dataPeriods[i].symbol.get('name'),
                                              precipitation=dataPeriods[i].precipitation.get('value'),
                                              wind=dataPeriods[i].windspeed.get('mps'),
                                              temp=dataPeriods[i].temperature.get('value'))
        return text

class Meteoblue(WeatherSite):
    def __init__(self, url, periods):
        super(Meteoblue, self).__init__(url, periods)
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', 'speed=METER_PER_SECOND;temp=CELSIUS'))
        self.xml = BeautifulSoup(opener.open(url))
        self.periodPattern = 'T{hour} {precipitation}mm ({probability}) {wind}m/s {temp}C '

    def generateText(self):
        text = self.xml.find(id='location_info').h1.string.replace('Weather', '') + ' ' + self.xml.find(class_='picto').find_all("tr")[0].th.string.split('.')[1][0:2] + ' '
        trs = self.xml.find(class_='picto').find_all("tr")
        for i in self.periods:
            text += self.periodPattern.format(hour=trs[0].find_all("td")[i].string.string[0:2],
                                              symbol=trs[1].find_all("td")[i]['class'][2],
                                              precipitation=trs[6].find_all("td")[i].string,
                                              probability=trs[7].find_all("td")[i].string,
                                              wind=trs[5].find_all("td")[i].string,
                                              temp=trs[2].find_all("td")[i].string.split('\t')[0])
        return text


class MountainForecast(WeatherSite):
    def __init__(self, url, periods):
        super(MountainForecast, self).__init__(url, periods)
        self.xml = BeautifulSoup(urllib2.urlopen(url))
        self.periodPattern = '{date}{time} {sybmol} {rain}mm {wind}km/h {temp1}-{temp2}C '

    def generateText(self):
        text = self.xml.find("nobr").text.split(',')[0] + ' '
        trs = self.xml.find(class_='forecasts')
        dates = trs.find(class_="lar hea ").find_all("td")
        times = trs.find_all(class_="tiny")
        desc = trs.find_all(class_="weathercell")
        rains = trs.find_all(class_="rain")
        winds = trs.find_all(class_="windcell")
        temps = trs.find_all(class_="temp")
        dateMod = {'AM': 0, 'PM': 1, 'night': 2}
        for i in self.periods:
            text += self.periodPattern.format(date=dates[(i+dateMod[times[0].text])/3].text.split()[0][:3],
                                              time=times[i].string,
                                              sybmol=desc[i].img['alt'],
                                              rain=rains[i].string,
                                              wind=winds[i].img['alt'].split()[0],
                                              temp1=temps[i+18].string,
                                              temp2=temps[i].string)
        return text
