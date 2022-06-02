from time import sleep
from Object.DownloadBase.Google.google_loading import GoogleBase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from Object.DownloadBase.Google.google_filter import GoogleMainFilter


class GetReasons(GoogleBase):

    def __init__(self, driver, main_filter):
        super().__init__(driver)
        self.main_filter = main_filter
        self.is_changed = False
        self.reasons = {}

    def get_reasons(self):
        print("不承認理由を抽出")
        max_item, this_item = self.get_current_and_max_items()
        if max_item > 500:
            if 'ポリシーの承認状況' not in self.main_filter:
                self.main_filter += "; ポリシーの承認状況: 承認済み（制限付き）、不承認"
                self.google_table_loading()
                GoogleMainFilter(self.driver, self.main_filter).set_main_filter()
                max_item, this_item = self.get_current_and_max_items()
                self.is_changed = True

        xxx = self.driver.wait_presence("//pagination-bar", 120).location_once_scrolled_into_view
        sleep(0.5)

        if this_item < max_item:
            self.select_500_items_per_page()

        self.move_down_and_up()

        rows = self.driver.get_elements("//*[text()='不承認' or text()='承認済み（制限付き）']//ancestor::div[@role='row']").iter()

        for row in rows:
            for ret in {1, 2}:
                try:
                    sleep(0.5)
                    e = row.find_element_by_xpath(".//*[text()='不承認' or text()='承認済み（制限付き）']")
                    chain = ActionChains(self.driver.driver_).move_to_element(e)
                    chain.click().perform()
                    cnt = 0
                    while True:
                        cnt += 1
                        try:
                            if cnt > 1:
                                sleep(0.1)
                                self.driver.wait_presence("//div[@aria-label='広告アセットの表']").send_keys(Keys.DOWN)
                            e.click()
                            break
                        except:
                            pass

                        if cnt > 10:
                            print("MOVE TO ELEMENT ERROR")
                            raise ValueError

                    self.google_table_loading()

                    reason = self.driver.wait_presence("//ad-asset-details-view//asset-status-popup//table-hover[contains(@class, 'visible')]//policy-topic").text

                    reason = reason.replace(chr(10), " ").replace(" ポリシーを確認", "").replace("error ", "")
                    asset_id = row.find_element_by_xpath(".//ess-cell[@essfield='asset_id']//text-field").text
                    try:
                        row.find_element_by_xpath(".//ess-cell[@essfield='asset_id']//text-field").click()
                    except:
                        pass
                    self.reasons[asset_id] = reason
                    break
                except:
                    pass

        print("不承認理由を抽出 OK")

        return self.reasons

    def select_500_items_per_page(self):
        self.driver.find_element_by_xpath("//pagination-bar//*[contains(text(), '表示する行')]"
                                          "//following-sibling::material-dropdown-select"
                                          "//dropdown-button").click()
        sleep(0.5)
        a = self.driver.wait_presence(
            "//material-list//material-select-dropdown-item[@role='option']//*[text()='500']")
        sleep(0.5)
        a.click()

        self.google_table_loading()

    def move_down_and_up(self):
        main_table = "//div[@aria-label='広告アセットの表']"

        self.driver.wait_presence(main_table).send_keys(Keys.END + Keys.PAGE_DOWN)
        sleep(0.5)

        # Mote to TOP
        self.driver.wait_presence(main_table).send_keys(Keys.HOME + Keys.PAGE_UP)
        for ree in range(3):
            self.driver.wait_presence(main_table).send_keys(Keys.PAGE_UP)
            sleep(0.5)

        sleep(1)
        self.google_table_loading()

    def get_current_and_max_items(self):
        selected_text = self.driver.wait_presence("//pagination-bar//*[contains(@class, 'selected')]"
                                                  "//div[contains(text(), ' 件中 ') and contains(text(), ' 件を表示')]").text

        max_item = int(selected_text.split(" 件中")[0].strip())

        fr, tr = selected_text.split(" 件中 ")[-1].replace(" 件を表示", "").split("～")
        this_item = int(tr.strip()) - int(fr.strip()) + 1
        xxx = self.driver.wait_presence("//pagination-bar").location_once_scrolled_into_view
        sleep(0.5)

        return max_item, this_item