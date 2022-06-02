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
    add_item = [{'f_name': 'hiyo'}, {'f_name': 'yosan'}, {'f_name': 'son'}]
    go = Google(task, lock=None)

    for item in add_item:
        time_list = []
        item.update(main_filter)
        go.inf.update(item)
        go.name_items = ['index', '__Sheet', 'account_id', 'f_name']
        print(item)

        if 'hiyo' in item['f_name']:
            # time_info = BasicTimeInfo("yesterday&today")
            go.info.bunkatsu = '時間帯,日'
            time_info = BasicTimeInfo("custom;20220530;20220531")
            print(f'hiyo : {time_info}')
            data_hiyo = go.run(time_info)
            data_son.loc[(data_son['キャンペーンのステータス' == "合計: フィルタしたキャンペーン" & '時間帯' != ''], "キャンペーン")] = "合計"
            data_hiyo.to_csv(os.path.join('./2_Processing', 'data_hi.csv'), encoding='UTF-16', sep='\t', index=False)

        else:
            go.info.bunkatsu = ''
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
            arr = []
            for time_info in time_list:
                if 'yosan' in item['f_name']:
                    print(f'data_yosan {time_info}')
                    tinf = BasicTimeInfo(time_info)
                    data_yosan = go.run(tinf)
                    data_yosan['date'] = tinf.dl_end_time_date.date()
                    data_yosan.loc[(data_yosan['キャンペーンのステータス' == "合計: フィルタしたキャンペーン"], "キャンペーン")] = "合計"
                    arr.append(data_yosan)
                if 'son' in item['f_name']:
                    print(f'data_son {time_info}')
                    tinf = BasicTimeInfo(time_info)
                    data_son = go.run(tinf)
                    data_son['date'] = tinf.dl_end_time_date.date()
                    data_son.loc[(data_son['キャンペーンのステータス' == "合計: フィルタしたキャンペーン"], "キャンペーン")] = "合計"
                    arr.append(data_son)

            data = pd.concat(arr, axis=0, ignore_index=True)
            data.to_csv(os.path.join('./2_Processing', f'{item["f_name"]}' + '.csv'), encoding='UTF-16', sep='\t', index=False)

    # for time_info in [BasicTimeInfo("This month"), BasicTimeInfo("Today"), BasicTimeInfo("Last 7 days")]:
    #     data = go.run(time_info)
    #     print(data)

