import datetime
import csv
import os

import pandas as pd

from app.downloader.google import Google
from app.time_info import BasicTimeInfo




def run_task(task):

    print(task)
    start_date = task["start_date"]
    cpn_gene = str(task["campaign_name"]).replace("\n", "、")
    main_filter = {f'main_filter': f'キャンペーンのステータス: すべて; 表示回数 > 0; キャンペーン: {cpn_gene}'}
    add_item = [{'分割': '時間帯,日', 'f_name': 'hiyo'}, {'分割': '', 'f_name': 'son'}, {'分割': '', 'f_name': 'yosan'}]
    go = Google(task, lock=None)

    for item in add_item:
        time_list = []
        time_info = ''
        item.update(main_filter)
        print(item)

        if 'hiyo' in item['f_name']:
            # time_info = BasicTimeInfo("yesterday&today")
            time_info = BasicTimeInfo("custom;20220530;20220531")
            go.inf.update(item)
            go.name_items = ['index', '__Sheet', 'account_id', 'f_name']
            print(f'hiyo : {time_info}')
            data_hiyo = go.run(time_info)
            data_hiyo.to_csv(os.path.join('./2_Processing', 'data_hi.csv'), encoding='UTF-16', sep='\t', index=False)

        else:
            if 'son' in item['f_name']:
                # now_date = datetime.datetime.today().strftime('%Y%m%d')
                now_date = datetime.datetime.strptime('2022/05/31', '%Y/%m/%d')
                gap_days = (now_date - start_date).days

                for i in range(0, gap_days + 1):
                    input_time = now_date - datetime.timedelta(days=i)
                    time_info = f'custom;{input_time.strftime("%Y%m%d")};{input_time.strftime("%Y%m%d")}'
                    time_list.append(time_info)
                print(f'son : {time_list}')

            if 'yosan'in item['f_name']:
                # now_date = datetime.datetime.today().strftime('%Y%m%d')
                now_date = datetime.datetime.strptime('2022/05/31', '%Y/%m/%d')
                gap_days = (now_date - start_date).days

                for i in range(0, gap_days + 1):
                    end_time = now_date - datetime.timedelta(days=i)
                    start_time = end_time - datetime.timedelta(days=7)
                    time_info = f'custom;{start_time.strftime("%Y%m%d")};{end_time.strftime("%Y%m%d")}'
                    time_list.append(time_info)
                print(f'yosan : {time_list}')

            data = pd.DataFrame()
            for time_info in time_list:
                if 'yosan' in item['f_name']:
                    print(f'data_yosan {time_info}')
                    data_yosan = go.run(BasicTimeInfo(time_info))
                if 'son' in item['f_name']:
                    print(f'data_son {time_info}')
                    data_son = go.run(BasicTimeInfo(time_info))
                data.append(data_son, ignore_index=True)
            data.to_csv(os.path.join('./2_Processing', f'{item["f_name"]}'), encoding='UTF-16', sep='\t', index=False)

    # for time_info in [BasicTimeInfo("This month"), BasicTimeInfo("Today"), BasicTimeInfo("Last 7 days")]:
    #     data = go.run(time_info)
    #     print(data)

