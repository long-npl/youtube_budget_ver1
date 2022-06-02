from app.downloader.google import Google
from app.time_info import BasicTimeInfo



def run_task(task):
    print(task)
    add_item = {'main_filter': 'キャンペーンのステータス: 有効のみ', 'template_change': '',
           'template_items': '表示回数,費用', '分割': '', 'f_name': 'son'}
    time_info = BasicTimeInfo("yesterday & today")
    go = Google(task, lock=None)
    go.inf.update(add_item)
    go.name_items = ['index', '__Sheet', 'account_id', 'f_name']

    data = go.run(time_info)
    print(data)

    # for time_info in [BasicTimeInfo("This month"), BasicTimeInfo("Today"), BasicTimeInfo("Last 7 days")]:
    #     data = go.run(time_info)
    #     print(data)

