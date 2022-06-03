import datetime
import os
import numpy as np
import pandas as pd
import xlwings as xw
from app.downloader.google import Google
from app.time_info import BasicTimeInfo
from time import sleep

class Paste:
    def __init__(self, data_hiyo, data_yosan_all, data_son_all, start_date, account_id, account_name, now_date):
        self.data_hiyo = data_hiyo
        self.data_yosan_all = data_yosan_all
        self.data_son_all = data_son_all
        self.app = xw.App(visible=True, add_book=False)
        self.books = self.app.books.open('./Ifmt/FMT.xlsx', read_only=True)
        self.ws_cost = self.books.sheets['【Youtube_Budget Adjuster】モニタリング']
        self.ws_hi = self.books.sheets['日別推移']
        self.start_date = start_date
        self.account_id = account_id
        self.account_name = account_name
        self.now_date = now_date
        # self.now_date = datetime.datetime.today().strftime('%Y/%m/%d')


    def paste_cost(self):
        self.ws_cost.select()
        data_hi = self.data_hiyo[self.data_hiyo['キャンペーン'] != ''].copy()
        data_son = self.data_son_all[(self.data_son_all['キャンペーン'] != '')].copy()
        data_yosan = self.data_yosan_all = self.data_yosan_all[self.data_yosan_all['キャンペーン'] != '']

        cpx = 0
        for cpn_name, cpn_data in data_hi.groupby(['キャンペーン'], dropna=False):
            if cpn_name == '合計 アカウント':
                base_col = 2
                self.ws_cost.range(4, 3).value = self.now_date
                self.ws_cost.range(5, 3).value = self.account_name
                self.ws_cost.range(6, 3).value = self.account_id
            else:
                cpx += 1
                base_col = cpx * 12 + 2
                paste_col = cpx * 12 + 2
                self.ws_cost.range((7, 2), (43, 11)).copy()
                self.ws_cost.range((7, paste_col), (43, paste_col + 11)).paste('all')  # paste range to next block
                self.ws_cost.api.Application.CutCopyMode = False
                self.ws_cost.range((7, paste_col)).column_width = self.ws_cost.range(2, 2).column_width

            self.ws_cost.range(7, base_col + 1).value = cpn_name
            self.ws_cost.range(17, base_col).value = self.now_date

            for i in range(0, len(data_yosan)):
                if data_yosan['キャンペーン'][i] == cpn_name and data_yosan['date'][i] == self.now_date.date():
                    self.ws_cost.range(10, base_col + 1).value = data_yosan['予算'][i]
                    break

            for i in range(0, len(data_son)):
                if data_yosan['キャンペーン'][i] == cpn_name and data_yosan['date'][i] == self.now_date.date():
                    self.ws_cost.range(14, base_col + 1).value = data_yosan['ディスプレイ広告の IS 損失率（予算）'][i]
                    break

            for sub_days, sub_data in cpn_data.groupby(['日']):
                sub_data['時間帯'] = sub_data['時間帯'].apply(lambda x: int(float(x)))
                sub_data.sort_values("時間帯", inplace=True)
                assert list(range(24)) == list(sub_data['時間帯']), "invalid sorting"

                if sub_days == self.now_date.strftime('%Y-%m-%d'):
                    tt_col = base_col + 1
                elif sub_days == (self.now_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d'):
                    tt_col = base_col
                else:
                    raise

                self.ws_cost.range(18, tt_col + 2).options(pd.Series, index=False, header=False, expand='table').value = sub_data['費用']
                self.ws_cost.range(18, tt_col + 7).options(pd.Series, index=False, header=False, expand='table').value = sub_data['平均インプレッション単価']


    def paste_hi(self):
        self.ws_hi.select()
        data = pd.concat([self.data_yosan_all, self.data_son_all], axis=1).drop_duplicates().reset_index(drop=True)
        _, i = np.unique(data.columns, return_index=True)
        data = data.iloc[:, i] # remove duplicate col
        data.sort_values('date', inplace=True)
        data = data[data['キャンペーン'] != '']
        data.to_csv(os.path.join('./2_Processing', 'all' + '.csv'), encoding='UTF-16', sep='\t',
                    index=False)
        row_v = (self.now_date - self.start_date).days
        self.ws_hi.range((8, 2), (8, 6)).copy()
        for k in range(9, row_v + 9):
            self.ws_hi.range((k, 2), (k, 6)).paste('all')

        cpx = 0
        for sub_cam, sub_da in data.groupby(['キャンペーン']):
            if sub_cam == '合計 アカウント':
                base_col = 2
            else:
                cpx += 1
                base_col = cpx * 6 + 2
                paste_col = cpx * 6 + 2
                self.ws_hi.range((6, 2), (row_v + 9, 6)).copy()
                self.ws_hi.range((6, paste_col)).paste('all')  # paste range to next block
                self.ws_hi.api.Application.CutCopyMode = False

            self.ws_hi.range(3, base_col + 1).value = sub_cam
            sub_da.sort_values("date", inplace=True)

            self.ws_hi.range(8, base_col).options(pd.Series, index=False, header=False, expand='table').value = sub_da['date']
            self.ws_hi.range(8, base_col+1).options(pd.Series, index=False, header=False, expand='table').value = sub_da['予算']
            self.ws_hi.range(8, base_col+2).options(pd.Series, index=False, header=False, expand='table').value = sub_da['費用']
            self.ws_hi.range(8, base_col+3).options(pd.Series, index=False, header=False, expand='table').value = sub_da['平均インプレッション単価']
            self.ws_hi.range(8, base_col+4).options(pd.Series, index=False, header=False, expand='table').value = sub_da['ディスプレイ広告の IS 損失率（予算）']
        self.ws_hi.select('A1')
        self.ws_cost.select('A1')


    def save(self):
        self.wb.save(f'./01.out/use_test.xlsx')
        self.wb.close()
        self.app.kill()



def run_task(task):

    print(task)
    start_date = task["start_date"]
    now_date = datetime.datetime.strptime('2022/05/31', '%Y/%m/%d')
    # now_date = datetime.datetime.today().strftime('%Y/%m/%d')
    gap_days = (now_date - start_date).days
    account_id = task["account_id"]
    account_name = task["account_name"]
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
            data_hiyo.loc[(data_hiyo['キャンペーンのステータス'] == '合計: フィルタしたキャンペーン') &
                          (data_hiyo['時間帯'] != ''), "キャンペーン"] = "合計 アカウント"
            data_hiyo['平均インプレッション単価'] = data_hiyo['平均インプレッション単価'].apply(lambda x: 0 if x == ' --' else x)
            data_hiyo['費用'] = data_hiyo['費用'].apply(lambda x: 0 if x == ' --' else x)
            data_hiyo.to_csv(os.path.join('./2_Processing', 'data_hi.csv'), encoding='UTF-16', sep='\t', index=False)

        else:
            go.info.bunkatsu = ''
            if 'yosan' in item['f_name']:
                for i in range(0, gap_days + 1):
                    input_time = now_date - datetime.timedelta(days=i)
                    time_info = f'custom;{input_time.strftime("%Y%m%d")};{input_time.strftime("%Y%m%d")}'
                    time_list.append(time_info)
                print(f'son : {time_list}')

            if 'son' in item['f_name']:
                for i in range(0, gap_days + 1):
                    end_time = now_date - datetime.timedelta(days=i)
                    start_time = end_time - datetime.timedelta(days=7)
                    time_info = f'custom;{start_time.strftime("%Y%m%d")};{end_time.strftime("%Y%m%d")}'
                    time_list.append(time_info)
                print(f'yosan : {time_list}')

            arr = []
            for time_info in time_list:
                if 'yosan' in item['f_name']:
                    print(f'data_yosan {time_info}')
                    tinf = BasicTimeInfo(time_info)
                    data_yosan = go.run(tinf)
                    data_yosan['date'] = tinf.dl_end_time_date.date()
                    data_yosan.loc[(data_yosan['キャンペーンのステータス'] == '合計: フィルタしたキャンペーン'), "キャンペーン"] = "合計 アカウント"
                    total_sum = data_yosan[data_yosan['予算'] != '']['予算'].astype(float).sum()
                    data_yosan.loc[(data_yosan['キャンペーンのステータス'] == '合計: フィルタしたキャンペーン'), '予算'] = total_sum
                    data_yosan['平均インプレッション単価'] = data_yosan['平均インプレッション単価'].apply(lambda x: 0 if x == ' --' else x)
                    data_yosan = data_yosan.drop('ディスプレイ広告の IS 損失率（予算）', axis=1)
                    arr.append(data_yosan)
                    data_yosan_all = pd.concat(arr, axis=0, ignore_index=True)

                if 'son' in item['f_name']:
                    print(f'data_son {time_info}')
                    tinf = BasicTimeInfo(time_info)
                    data_son = go.run(tinf)
                    data_son['date'] = tinf.dl_end_time_date.date()
                    data_son.loc[(data_son['キャンペーンのステータス'] == "合計: フィルタしたキャンペーン"), "キャンペーン"] = "合計 アカウント"
                    total_sum = data_son[data_son['予算'] != '']['予算'].astype(float).sum()
                    data_son.loc[(data_son['キャンペーンのステータス'] == '合計: フィルタしたキャンペーン'), '予算'] = total_sum
                    data_son['ディスプレイ広告の IS 損失率（予算）'] = data_son['ディスプレイ広告の IS 損失率（予算）'].apply(lambda x: '0.0%' if x == ' --' else x)
                    data_son = data_son.drop('平均インプレッション単価', axis=1)
                    arr.append(data_son)
                    data_son_all = pd.concat(arr, axis=0, ignore_index=True)


            data = pd.concat(arr, axis=0, ignore_index=True)
            data.to_csv(os.path.join('./2_Processing', f'{item["f_name"]}' + '.csv'), encoding='UTF-16', sep='\t', index=False)

    paste_v = Paste(data_hiyo, data_son_all, data_yosan_all, start_date, account_id, account_name, now_date)
    paste_v.paste_hi()
    paste_v.paste_cost()

    # for time_info in [BasicTimeInfo("This month"), BasicTimeInfo("Today"), BasicTimeInfo("Last 7 days")]:
    #     data = go.run(time_info)
    #     print(data)
