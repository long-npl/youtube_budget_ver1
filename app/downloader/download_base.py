import functools
import logging
import os
import shutil
import uuid

import pandas
from pydantic import BaseModel, Field

from app.commons import CHROME
from app.downloader.download_exc import NotAppliedMethod, apply_class_decorator
from app.downloader.folder_utils import download_and_move

logger = logging.getLogger(__name__)


class DownloadInfo:
    def __init__(self, time_info, file_name, time_format):
        self.dl_st = time_info.dl_start_time_date.date()
        self.dl_ed = time_info.dl_end_time_date.date()
        self.dl_start_time = self.dl_st.strftime(time_format)
        self.dl_end_time = self.dl_ed.strftime(time_format)
        self.file_name = file_name


class LoginBase(BaseModel):
    login_id: str
    login_pw: str
    keep_open: str = Field("Close", alias="Keep_Open")


class DownloadBase:
    name_items: list = ['__Sheet', 'index']

    def __init__(self, inf, lock):
        """initialize downloader"""
        self.inf = inf
        self.raw_folder = inf['raw_folder']
        self.re_download = inf.get("re_download", "ON") == "ON"
        self.wait_time = int(inf.get("Wait_Time", 180))
        self.lock = lock
        self._download_folder_path = None

    @functools.cached_property
    def download_folder_path(self):
        """generate download folder path"""
        path = os.path.join(self.raw_folder, "1_Raw", f"{self.inf['__Sheet']}_{self.inf['index']}_{uuid.uuid4().hex}")
        os.makedirs(path)
        return path

    def generate_file_name(self, time_info):
        """generate raw_data file_name"""
        not_found = [col for col in self.name_items if col not in self.inf]
        assert len(not_found) == 0, f"file_name info not found: {not_found}"
        file_name = "_".join(str(self.inf[item]) for item in self.name_items) + f"_{time_info.dl_start_time}_{time_info.dl_end_time}.csv"
        for s in r'\/:*?"<>|':
            file_name = file_name.replace(s, "")
        return file_name

    def read_old_file(self, file_name, folder=None, re_download=None):
        """read raw data from old file"""
        folder = folder or self.raw_folder
        re_download = re_download if isinstance(re_download, bool) else self.re_download
        path = os.path.join(folder, file_name)

        file_exists = os.path.exists(path)
        if file_exists and re_download:
            os.unlink(path)
            file_exists = False

        data = None
        if file_exists:
            try:
                data = pandas.read_csv(path, encoding="UTF-16", sep="\t", index_col=False, thousands=",",
                                       keep_default_na=False, dtype=object)
                data.fillna("", inplace=True)
            except:
                data = None

        return data

    def main_process(self, time_info, file_name):
        raise NotAppliedMethod()

    def convert_time_info(self, time_info, file_name, time_format):
        return DownloadInfo(time_info, file_name, time_format)

    def clean_up_folder(self):
        if os.path.exists(self.download_folder_path):
            shutil.rmtree(self.download_folder_path)
        os.makedirs(self.download_folder_path, exist_ok=True)
        check_file = len(os.listdir(self.download_folder_path))
        assert check_file == 0, f"files are not allowed in download folder, found: {check_file}"

    def download_and_move(self, folder, file_name,  file_check=None, ext='.csv'):
        return download_and_move(self.download_folder_path, folder, file_name, file_check, ext, self.wait_time)

    def __del__(self):
        """close chrome_driver"""
        driver = self.__dict__.get("driver")
        if isinstance(driver, CHROME):
            driver.quit()

    def run(self, time_info):
        file_name = self.generate_file_name(time_info)
        data = self.read_old_file(file_name)
        if data is None:
            data = self.main_process(time_info, file_name)
            data.to_csv(os.path.join(self.raw_folder, file_name), encoding='UTF-16', sep='\t', index=False)
        return data


