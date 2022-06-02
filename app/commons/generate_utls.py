import pandas
import datetime
from dateutil.relativedelta import relativedelta


def generate_date_list(start_time, end_time):
    """
    :return: list of date from start_time to end_time
    """
    return [d.date() for d in pandas.date_range(start_time, end_time).to_pydatetime()]


def generate_month_list(start_time, end_time):
    """
    :return: list of month with format of %Y%m from start_time to end_time,
    """
    month_list = []
    st = start_time
    while True:
        ed = (st + relativedelta(months=1)).replace(day=1) - datetime.timedelta(days=1)
        if ed > end_time:
            ed = end_time

        assert st.strftime('%Y%m') == ed.strftime("%Y%m"), "Collect Time Error"

        month_list.append((st, ed, st.strftime("%Y%m")))

        st = ed + datetime.timedelta(days=1)
        if st > end_time:
            break

    return month_list
