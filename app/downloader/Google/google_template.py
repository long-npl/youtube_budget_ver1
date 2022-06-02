from time import sleep
from selenium.webdriver.common.keys import Keys
from app.downloader.Google.google_loading import GoogleBase


class GoogleTemplate(GoogleBase):
    def __init__(self, driver, template, template_change, template_items):
        super().__init__(driver)
        self.template = template
        self.template_change = template_change
        self.template_items = template_items

    def get_current_columns(self):
        return self.driver.get_elements("//reorder-list//selected-column"
                                        "//div[contains(@class,'deselect-icon-decorator')]")

    def reset_columns(self):
        current_columns = self.get_current_columns()
        sleep(1)
        for item in current_columns:
            item.click()

        if not not self.get_current_columns():
            raise AssertionError("Reset template columns failed")

    def add_column(self, header_name):
        sleep(0.25)
        self.driver.wait_visible("//column-selector"
                                 "//material-icon//i[@aria-label='表示項目の検索']").click()
        sleep(0.25)
        self.driver.wait_visible("//input[@placeholder = '検索']", 20).clear_and_type(header_name)
        sleep(1)
        for suggest_item in self.driver.get_elements("//highlighted-text"):
            if suggest_item.text == header_name:
                suggest_item.click()
                break
        else:
            print(f"Add col {header_name} to template error")
            self.driver.wait_visible("//input[@placeholder = '検索']").send_keys(Keys.ENTER)

    def reset_bunkatsu(self):
        if len(self.driver.get_elements("//ad-assets-header//*[text()='アプリ エンゲージメント広告']")) > 0 or \
                'demographics/combinations' in self.driver.current_url:
            pass
        else:
            self.driver.wait_clickable("//material-menu[contains(@class, 'toolbelt-segmentation-menu')]", 15).click()
            sleep(0.5)
            self.driver.wait_clickable("//material-select-item[@aria-label='なし']", 15).click()
            sleep(1)

    def add_template(self):
        # Add Template
        try:
            self.driver.wait_presence("//material-select-item[@aria-label='表示項目の変更']", 10).click()
        except:
            pass

        sleep(0.5)

        self.reset_columns()

        for hed in self.template_items.split(","):
            self.add_column(hed)

        self.driver.wait_presence("//material-checkbox[contains(@class,'save-columns-checkbox')]", 10).click()
        self.driver.wait_presence("//span[text()='表示項目の設定を保存']/ancestor::label/input", 10).send_keys(self.template)
        self.driver.wait_presence("//material-button[div='保存して適用']", 10).click()
        sleep(0.5)
        chikan_check = "//*[text()='表示項目セットの置き換え']/ancestor::focus-trap//*[text()='置換']/parent::material-button"
        check_box = self.driver.get_elements(chikan_check)
        if len(check_box) > 0:
            self.driver.get_element(chikan_check).click()

    def choose_template(self):
        self.driver.wait_clickable("//material-menu[contains(@class, 'column-customization-menu-item')]", 10).click()
        sleep(2)
        try:
            if self.template_change == "ON":
                return False
            else:
                sleep(0.5)
                self.driver.wait_presence(f"//material-select-item//span[text()='{self.template}']", 6)
                sleep(1)
                self.driver.wait_clickable(f"//material-select-item//span[text()='{self.template}']", 15).click()
                return True
        except:
            return False

    def select_template(self):
        # 分割をReset
        try:
            sleep(0.5)
            self.google_table_loading()
            sleep(0.5)

            self.reset_bunkatsu()

            self.google_table_loading()

            if self.template == "":
                return True

            if not self.choose_template():
                if self.template_items == '':
                    print(f"No template: {self.template}")
                    return False
                else:
                    self.add_template()

            if len(self.driver.get_elements("//material-button[@aria-label='グラフを非表示']")) > 0:
                self.driver.get_element("//material-button[@aria-label='グラフを非表示']").click()

            return True
        except Exception as ee:
            print(ee)
            return False

    def select_template_process(self):
        sleep(1)
        if not self.select_template():
            if not self.select_template():
                raise ValueError("Select Template Error")


