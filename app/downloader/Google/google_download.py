from time import sleep
import pandas
import os
from app.downloader.Google.google_loading import GoogleBase
from app.downloader.folder_utils import download_and_move


class GoogleDownload(GoogleBase):
    def __init__(self, driver, tab, bunkatsu_items, download_folder_path, raw_folder, file_name, exclude="除外"):
        super().__init__(driver)
        self.tab = tab
        self.bunkatsu_items = bunkatsu_items
        self.download_folder_path = download_folder_path
        self.raw_folder = raw_folder
        self.file_name = file_name
        self.header_row = 2 if self.tab == 'reporting/reporteditor/view' else 0
        self.exclude_header_row = "除外"
        self.exclude_total_row = "Deo jogai"

    def report_download(self):
        self.driver.wait_visible("//report-editor//material-button[contains(@class, 'download-icon')]", 10).click()
        sleep(1)
        self.driver.wait_visible("//div[contains(@pane-id,'GINSU')]//material-list-item[text()='Excel .csv']", 10).click()
        sleep(1)

        try:
            self.driver.wait_presence("//*[text()='レポートを準備しています']", 6)
        except:
            try:
                self.driver.wait_visible("//div[contains(@pane-id,'GINSU')]//material-list-item[text()='Excel .csv']", 10).click()
            except:
                pass

    def checked_or_not(self, element):
        return self.driver.wait_visible(element, 10).get_attribute("aria-checked")

    def total_row_remove(self):
        if self.exclude_total_row == "除外":
            check_box = "//advanced-download//div[text()='集計行' or text()='合計']//ancestor::material-checkbox"

            if self.checked_or_not(check_box) == "true":
                self.driver.wait_visible(check_box).click()
                sleep(0.05)

            if self.checked_or_not(check_box) == "true":
                raise AssertionError

    def header_remove(self):
        if self.exclude_header_row == "除外":
            check_box = "//div[@pane-id]//div[text()='タイトルと期間']/ancestor::material-checkbox"

            if self.checked_or_not(check_box) == "true":
                self.driver.wait_visible(check_box).click()
                sleep(0.05)

            if self.checked_or_not(check_box) == "true":
                raise AssertionError

    def add_bunkatsu(self):
        title_and_duration_checkbox = "//div[@pane-id]//div[text()='タイトルと期間']/ancestor::material-checkbox"
        add_segment = title_and_duration_checkbox + "/ancestor::zippy//multi-suggest-input//*[@placeholder='セグメントを追加します']"

        # Clear Selected 分割
        selected = "//advanced-download//material-chips//material-chip//*[@aria-label='削除' and @role='button']"
        for ele in self.driver.find_elements_by_xpath(selected):
            ele.click()
            sleep(0.3)

        self.driver.wait_visible(add_segment, 6).clear()  # Clear add segment

        if self.bunkatsu_items == "":
            return

        for item in self.bunkatsu_items.split(','):
            self.driver.wait_visible(add_segment, 10).send_keys(item)
            select_item = f"//div[@pane-id]//span[text()='{item}']/parent::material-select-item[@role='option']"
            self.driver.wait_visible(select_item, 10).click()
            sleep(0.8)
        self.driver.wait_visible("//span[text()='分類して表示']", 6).click()

    def wait_generate(self):
        try:
            self.driver.wait_invisible("//*[text()='レポートを準備しています']", 120)
        except:
            pass

    def dashboard_download(self):
        sleep(1)

        self.driver.wait_visible("//span[text()='ダウンロード']/ancestor::material-button", 6).click()
        sleep(0.5)
        self.driver.wait_visible("//span[text()='その他のオプション']/ancestor::material-select-item", 6).click()
        sleep(0.5)

        self.total_row_remove()  # Remove 合計
        self.header_remove()  # Remove Header
        self.add_bunkatsu()  # 分割を追加

        # Click Download
        self.driver.wait_visible("//div[@pane-id]//material-yes-no-buttons//"
                                 "div[text()='ダウンロード']/parent::material-button", 6).click()
        sleep(1)

    def download_process(self, wait_time=180, adding_info=None, write_file=True):
        if adding_info is None:
            adding_info = {}

        if self.tab == 'reporting/reporteditor/view':
            self.report_download()
        else:
            self.dashboard_download()

        self.wait_generate()

        os.makedirs(os.path.join(self.raw_folder, "1_Raw"), exist_ok=True)
        download_and_move(self.download_folder_path, os.path.join(self.raw_folder, "1_Raw"), self.file_name, wait_time=wait_time)

        output = pandas.read_csv(os.path.join(self.raw_folder, "1_Raw", self.file_name), header=self.header_row, sep='\t',
                                 encoding="UTF-16", thousands=",", low_memory=False)
        output.fillna("", inplace=True)

        if len(adding_info) > 0:
            for key, value in adding_info.items():
                output[key] = value

        if write_file:
            output.to_csv(os.path.join(self.raw_folder, self.file_name), sep='\t', encoding="UTF-16", index=False)

        return output
