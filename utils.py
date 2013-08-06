from datetime import datetime
from model import Task
import settings

def addTask(phone, url, periods, sendDateTimeList, smsType, smsSender):
    task = Task(phone=phone,
                url=url,
                periods=map(
                int, periods.split(';')),
                sendDateTimeList=[datetime.strptime(dateString.strip(), settings.TIMEFORMAT) for dateString in sendDateTimeList.split(';') if dateString.strip()],
                smsType=smsType.strip(),
                smsSender=smsSender.strip())
    task.put()
