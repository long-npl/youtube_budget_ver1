import pandas
import datetime
import os
import sys
from youtube_budget import run_task
import pydantic


local_path = os.path.abspath(os.path.dirname(sys.argv[0]))  # Get local path
today_string = datetime.datetime.now().strftime("%Y%m%d")


def get_projects():
    prjs = pandas.read_excel(os.path.join(local_path, './Setting.xlsm'),
                             sheet_name="Google", index_col=False, engine="openpyxl", header=0,
                             keep_default_na=False, dtype=object)
    prjs['raw_folder'] = './1_In'
    prjs['out_folder'] = './2_Out'
    prjs['index'] = prjs.index
    prjs = prjs[prjs['Status(ON)'] == "ON"].reset_index(drop=True)
    list_v = {'__Sheet': 'Google', 'login_id': 'vu_van_cuong@ca-adv.co.jp', 'login_pw': '',
              'tab': 'campaigns', 'template': 'yb', 'channel': '', 'campaign_status': 'すべて', 'adgroup_status': 'すべて',
              'template_items': '平均インプレッション単価,費用,ディスプレイ広告のインプレッション シェア損失率（予算）',
              'view': '', 'template_change': 'ON', '分割': '', 'f_name': '', 'main_filter': ''
              }

    prjs_dict_list = list(prjs.apply(dict, 1))
    [prjs_dict.update(list_v) for prjs_dict in prjs_dict_list]


    return prjs_dict_list


def main():
    task_list = list(get_projects())
    for task in task_list:
        run_task(task)


if __name__ == "__main__":
    main()
