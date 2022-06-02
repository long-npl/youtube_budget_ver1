from app.downloader.google import Google
from app.time_info import BasicTimeInfo




def run_task(task):
    print(task)
    start_date = task["start_date"]
    cpn_gene = str(task["campaign_name"]).replace("\n", "、")
    main_filter = {f'main_filter': f'キャンペーンのステータス: すべて; 表示回数 > 0; キャンペーン: {cpn_gene}'}
    add_item = [{'分割': '時間帯,日', 'f_name': 'hi'}, {'分割': '', 'f_name': 'son'}, {'分割': '', 'f_name': 'yosan'}]
    go = Google(task, lock=None)
    for item in add_item:
        print(item)
        item.update(main_filter)
        if {'f_name': 'hi'} in item:
            time_info = BasicTimeInfo("custom;20220530;20220531")
            go.inf.update(item)
            go.name_items = ['index', '__Sheet', 'account_id', 'f_name']
            data_hi = go.run(time_info)
            print(data_hi)





    # for time_info in [BasicTimeInfo("This month"), BasicTimeInfo("Today"), BasicTimeInfo("Last 7 days")]:
    #     data = go.run(time_info)
    #     print(data)

