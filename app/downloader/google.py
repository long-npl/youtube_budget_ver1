import functools

from app.downloader.Google.google_filter import GoogleFullFilter, GoogleMainFilter
from app.downloader.Google.google_download import GoogleDownload
from app.downloader.Google.google_time import GoogleTimeSelect
from app.downloader.Google.google_login import GoogleLogin
from app.downloader.Google.google_template import GoogleTemplate
from app.downloader.Google.google_loading import GoogleBase
from app.downloader.download_base import DownloadBase
from pydantic import BaseModel, validator, Field
from enum import Enum

channels = {
    '検索': 1,
    'ディスプレイ': 2,
    'ショッピング': 3,
    '動画': 4,
    'アプリ': 7,
    'ローカル': 10,
    'ファインド': 11,
    'PMAX': 13,
    'パフォーマンス最大化': 13,
}


class StatusValues(str, Enum):
    all = "すべて"
    accept_deleted = "削除済みを除くすべて"
    yuukou = "有効のみ"


class GoogleInfo(BaseModel):
    login_id: str
    login_pw: str
    account_id: str
    ocid: str

    tab: str
    channel: str
    campaign_status: StatusValues
    adgroup_status: StatusValues
    main_filter: str

    template: str
    template_change: str
    template_items: str
    view: str = ""

    bunkatsu: str = Field(..., alias="分割")

    is_set = False

    class Config:
        use_enum_values = True
        keep_untouched = (functools.cached_property,)

    @validator("channel")
    def validate_channel(cls, v):
        return "" if v == "" else f"&channel={channels[v]}"

    @functools.cached_property
    def link(self):
        if self.tab == "reporting/reporteditor/view":
            link = f"https://ads.google.com/aw/{self.tab}?ocid={self.ocid}&reportId={self.template}"
        else:
            link = f"https://ads.google.com/aw/{self.tab}?ocid={self.ocid}{self.channel}"
        return link


class Google(DownloadBase, GoogleBase):

    @functools.cached_property
    def info(self):
        return GoogleInfo(**self.inf)

    @functools.cached_property
    def driver(self):
        driver = GoogleLogin(login_id=self.info.login_id, login_pw=self.info.login_pw, account_id=self.info.account_id,
                             link=self.info.link, download_folder_path=self.download_folder_path).login_process()

        if driver is None:
            raise ValueError("google login process error")

        return driver

    @functools.cached_property
    def is_set(self):
        return False

    def google_set_time(self, dl_info):
        GoogleTimeSelect(driver=self.driver, dl_info=dl_info).select_time_process()

    def google_filter(self):
        GoogleFullFilter(driver=self.driver, tab=self.info.tab, view=self.info.view, main_filter=self.info.main_filter,
                         side_status_dict={'campaign_status': self.info.campaign_status,
                                           'adgroup_status': self.info.adgroup_status},
                         is_account_mark=(
                                 self.info.template == "ADG_アカウント採点" and self.info.channel == "ディスプレイ")).set_total_filter()

    def select_template(self, template, should_change_template, template_items):
        GoogleTemplate(driver=self.driver,
                       template=template,
                       template_change=should_change_template,
                       template_items=template_items).select_template_process()

    def google_main_filter(self, check_texts=None, force_reset=False):
        GoogleMainFilter(driver=self.driver, main_filter=self.info.main_filter).set_main_filter_proc(
            check_texts=check_texts, force_reset=force_reset)

    def google_template(self):
        GoogleTemplate(driver=self.driver, template=self.info.template, template_change=self.info.template_change,
                       template_items=self.info.template_items).select_template_process()

    def google_download(self, file_name, adding_info=None, write_file=True):
        return GoogleDownload(driver=self.driver, tab=self.info.tab, bunkatsu_items=self.info.bunkatsu,
                              download_folder_path=self.download_folder_path, raw_folder=self.raw_folder,
                              file_name=file_name).download_process(adding_info=adding_info, write_file=write_file)

    def google_download_bunkatsu_assign(self, bunkatsu_split, file_name):
        return GoogleDownload(driver=self.driver, tab=self.info.tab, bunkatsu_items=bunkatsu_split,
                              download_folder_path=self.download_folder_path, raw_folder=self.raw_folder,
                              file_name=file_name).download_process()

    def google_set_up(self):
        self.google_table_loading()
        if self.info.tab != 'reporting/reporteditor/view':
            self.google_filter()
            self.google_template()

    def main_process(self, time_info, file_name):
        dl_info = self.convert_time_info(time_info, file_name, "%Y/%m/%d")  # 統括
        # Select Time
        if not self.info.is_set:
            self.google_set_up()
            self.info.is_set = True
        self.google_set_time(dl_info)
        return self.google_download(file_name=dl_info.file_name, adding_info={'__account_id': self.info.account_id,
                                                                              '__media': 'Google'})

"""
inf = {'raw_folder': r'./1_Raw', '__Sheet': 'Google', 'index': 0,
       'login_id': 'vu_van_cuong@ca-adv.co.jp', 'login_pw': '', 'account_id': '961-120-9976', 'ocid': '42373038',
       'tab': 'campaigns', 'template': 'TestForLong', 'channel': '',
       'campaign_status': 'すべて',
       'adgroup_status': 'すべて', 'main_filter': 'キャンペーンのステータス: 有効のみ', 'view': '', 'template_change': '',
       'template_items': '表示回数,費用', '分割': '', 're_download': 'OFF'
       }

a = Google(inf, lock=None)
a.name_items = ['f_name']
from app.time_info import BasicTimeInfo

time_info = BasicTimeInfo("This month")

for time_info in [BasicTimeInfo("This month"), BasicTimeInfo("Today"), BasicTimeInfo("Last 7 days")]:
    data = a.run(time_info)
    print(data)
"""