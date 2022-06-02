import datetime
from dateutil.relativedelta import relativedelta
from app.commons.parse_date import parse

today_string = datetime.datetime.now().strftime("%Y%m%d")

today = datetime.datetime.today()


def time_convert(time_string):
    if time_string == "lastmonth":
        end_date_time = today - datetime.timedelta(days=today.day)
        start_date_time = end_date_time - datetime.timedelta(days=end_date_time.day - 1)
    elif time_string.lower() == 'yesterday':
        end_date_time = today - datetime.timedelta(days=1)
        start_date_time = today - datetime.timedelta(days=1)
    elif time_string.lower() == 'today':
        end_date_time = today
        start_date_time = today
    elif "custom" in time_string:
        end = time_string.split(';')[-1]
        if end == "yesterday":
            end_date_time = today - datetime.timedelta(days=1)
        else:
            end_date_time = datetime.datetime.strptime(end, "%Y%m%d")
        start_date_time = datetime.datetime.strptime(time_string.split(';')[1], "%Y%m%d")
    elif time_string.startswith("last") and time_string.endswith("days"):
        step = int(time_string.replace("last", "").replace("days", ""))
        end_date_time = today - datetime.timedelta(days=1)
        start_date_time = today - datetime.timedelta(days=step)
    elif time_string == "thismonth":
        end_date_time = today - datetime.timedelta(days=1)
        start_date_time = today - datetime.timedelta(days=end_date_time.day)
    elif time_string == "thismonth(includetoday)":
        end_date_time = today
        start_date_time = today - datetime.timedelta(days=(end_date_time.day - 1))
    elif time_string == "yesterday&today":
        end_date_time = today
        start_date_time = today - datetime.timedelta(days=1)
    elif time_string.startswith("last") and time_string.endswith("months"):
        step = int(time_string.replace("last", "").replace("months", ""))
        end_date_time = today - datetime.timedelta(days=1)
        start_date_time = end_date_time.replace(day=1) - relativedelta(months=step - 1)
    elif time_string.startswith("last") and time_string.endswith("months(includetoday)"):
        step = int(time_string.replace("last", "").replace("months(includetoday)", ""))
        end_date_time = today
        start_date_time = end_date_time.replace(day=1) - relativedelta(months=step - 1)
    else:
        try:
            start_date_time, end_date_time = parse(time_string), parse(time_string)
        except:
            raise ValueError("Wrong Time String: {}".format(time_string))

    return [start_date_time,
            end_date_time,
            datetime.datetime.strftime(start_date_time, '%Y/%m/%d'),
            datetime.datetime.strftime(end_date_time, '%Y/%m/%d')]


class BasicTimeInfo:
    def __init__(self, time_string):
        self.time_string = str(time_string).lower().replace(" ", "")
        self.start_time_date, self.end_time_date, self.start_time, self.end_time = time_convert(self.time_string)
        self.dl_start_time_date, self.dl_end_time_date, self.dl_start_time, self.dl_end_time = time_convert(self.time_string)

