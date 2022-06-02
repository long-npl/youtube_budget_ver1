from app.commons.parse_date import parse
from selenium.webdriver.common.keys import Keys
from time import sleep
from app.downloader.Google.google_loading import GoogleBase
import datetime


class GoogleTimeSelect(GoogleBase):
    _end_date_input = "//material-input[contains(@class, 'end date-input')]//input"
    _start_date_input = "//material-input[contains(@class, 'start date-input')]//input"
    _date_picker = "//material-date-range-picker//dropdown-button//i | //div[@navi-id='datepicker']"
    _current_date = "//material-date-range-picker//span[contains(@class, 'button-text')]"

    def __init__(self, driver, dl_info):
        super().__init__(driver)
        self.dl_info = dl_info
        self.st = parse(self.dl_info.dl_start_time).date()
        self.ed = parse(self.dl_info.dl_end_time).date()
        self.time_indicator = self.convert_time_indicator()  # One Time Only
        self.is_time_changed = False

    def convert_time_indicator(self):
        if self.st.strftime("%Y%m%d") == self.ed.strftime("%Y%m%d"):
            indicator_text = f'{self.st.year}年{self.st.month}月{self.st.day}日'
        elif self.st.strftime("%Y%m") == self.ed.strftime("%Y%m"):
            indicator_text = f'{self.st.year}年{self.st.month}月{self.st.day}日～{self.ed.day}日'
        elif self.st.strftime("%Y") == self.ed.strftime("%Y"):
            indicator_text = f'{self.st.year}年{self.st.month}月{self.st.day}日～{self.ed.month}月{self.ed.day}日'
        else:
            indicator_text = f'{self.st.year}年{self.st.month}月{self.st.day}日～{self.ed.year}年{self.ed.month}月{self.ed.day}日'
        return indicator_text

    def get_current_date_text(self):
        return self.driver.wait_visible(self._current_date, 10).text

    def get_account_start_time(self):
        try:
            self.driver.wait_visible("//div[@navi-id='datepicker']", 15).click()
            sleep(1)
            self.driver.wait_clickable("//div[contains(@pane-id, 'CM')]//date-range-editor//material-select-item[@aria-label='全期間']", 15).click()
            self.driver.wait_visible("//material-date-range-picker//div[contains(@class,'range-title') and text()='全期間']", 15)
            account_all_time = self.driver.wait_visible("//material-date-range-picker//span[contains(@class, 'button-text')]").text
            return account_all_time
        except:
            return False

    def fill_time(self, date_input, date):
        sleep(1)
        self.driver.wait_visible(date_input, 6).click()
        sleep(0.1)
        self.driver.wait_visible(date_input, 6).clear_and_type(date + Keys.RETURN)

    def apply_time(self):
        try:
            self.driver.wait_visible("//date-range-editor/following-sibling::div//div[text()='適用']"
                                     "/parent::material-button", 3).click()
        except:
            self.driver.wait_visible("//date-range-editor/following-sibling::div//div[text()='適用']"
                                     "/following-sibling::material-ripple", 3).click()

    def select_time(self):
        try:
            self.google_table_loading()

            report_tab = "reporting/reporteditor/view" in self.driver.current_url

            retried = 0
            while (date_text := self.get_current_date_text()) != self.time_indicator and retried < 4:
                print(date_text)
                if (retried == 0 or retried == 2) and report_tab:
                    collection = ((self._end_date_input, self.dl_info.dl_end_time), (self._start_date_input, self.dl_info.dl_start_time))
                else:
                    collection = ((self._start_date_input, self.dl_info.dl_start_time), (self._end_date_input, self.dl_info.dl_end_time))
                self.driver.wait_visible(self._date_picker).click()
                sleep(1)

                for (date_input, date) in collection:
                    self.fill_time(date_input, date)
                sleep(1)
                self.apply_time()
                sleep(1)
                retried += 1
                self.google_table_loading()

            if date_text == self.time_indicator:
                return True
            else:
                print(f"Expect: {self.time_indicator}\nTime: {date_text}")
                return False
        except Exception as e:
            print(e)
            return False

    def reselect_start_time(self):
        account_start_time = self.get_account_start_time()
        if not account_start_time:
            raise AssertionError("Get 全期間 Failed")

        new_start_time = datetime.datetime.strptime(str(account_start_time).split("～")[0], "%Y年%m月%d日").date()
        if new_start_time > self.st:
            print(f"全期間: {new_start_time}, Convert Start Time from {self.st} to {new_start_time}")
            self.st = new_start_time
            self.dl_info.dl_start_time = self.st.strftime("%Y/%m/%d")
            self.time_indicator = self.convert_time_indicator()
            self.is_time_changed = True

    def select_time_process(self):
        if not self.select_time():
            if not self.select_time():
                raise ValueError("Select Time Error")
        print("Select Time OK")


