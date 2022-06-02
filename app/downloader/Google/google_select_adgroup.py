from app.commons.parse_date import parse
from selenium.webdriver.common.keys import Keys
from time import sleep
from app.downloader.Google.google_loading import GoogleBase
from app.downloader.Google.google_filter import GoogleSideFilter


class GoogleSelectAdgroup(GoogleBase):
    def __init__(self, driver, ocid, account_id, campaign_id, adgroup_id, campaign_name, adgroup_name,
                 side_campaign_status="削除済みを除くすべて", side_adgroup_status="削除済みを除くすべて"):
        super().__init__(driver)
        self.ocid = ocid
        self.side_campaign_status = side_campaign_status
        self.side_adgroup_status = side_adgroup_status
        self.side_filter_caller = GoogleSideFilter(self.driver, 'adassets', {}, False)
        self.account_id = account_id
        self.campaign_id = campaign_id
        self.adgroup_id = adgroup_id
        self.campaign_name = campaign_name
        self.adgroup_name = adgroup_name
        self.this_campaign = f"//awsm-campaign-tree//a[contains(@class, 'campaign-item') and @title='{campaign_name}']"
        self.this_adgroup = f"{self.this_campaign}/following-sibling::div[contains(@class, 'ad-group-items')]" \
                            f"//div[contains(@class, 'ad-group-item-title') and @title='{adgroup_name}']"
        self.select_this_campaign = f"{self.this_campaign}/material-ripple"
        self.select_this_adgroup = f"{self.this_adgroup}/material-ripple"
        self.this_adgroup_selected = f"{self.this_campaign}/following-sibling::div[contains(@class, 'ad-group-items')]" \
                                     f"//div[contains(@class, 'ad-group-item-title') " \
                                     f"and @title='{adgroup_name}' and contains(@class, 'selected')]"
        self.adgroup_list = f"{self.this_campaign}/following-sibling::div[contains(@class, 'ad-group-items')]/a"
        self.load_more_adgroup = f"{self.this_campaign}/following-sibling::div[contains(@class, 'ad-group-items')]" \
                                 "/div[contains(@class, 'ad-group-load-more campaign-child')]"
        self.load_more_campaign = "//awsm-campaign-tree//awsm-campaign-section" \
                                  "//div[contains(@class, 'campaign-load-more')]"

    def unhide_tab_bar(self):
        if len(self.driver.find_elements_by_xpath("//material-button[@aria-label='スコープ ナビゲーションのメニューを表示']")) > 0:
            self.driver.find_element_by_xpath("//material-button[@aria-label='スコープ ナビゲーションのメニューを表示']").click()
            sleep(0.5)

    def close_window_tabs(self):
        if len(self.driver.window_handles) > 1:
            while len(self.driver.window_handles) > 1:
                self.driver.switch_to_window(self.driver.window_handles[-1])
                self.driver.close()
            self.driver.switch_to_window(self.driver.window_handles[0])

    def click_select_campaign(self):
        if len(self.driver.find_elements_by_xpath("//material-button[@aria-label='スコープ ナビゲーションのメニューを表示']")) > 0:
            self.driver.find_element_by_xpath("//material-button[@aria-label='スコープ ナビゲーションのメニューを表示']").click()
            sleep(0.5)

        count = 0
        while len(self.driver.find_elements_by_xpath(self.adgroup_list)) == 0 and count <= 3:
            if len(self.driver.find_elements_by_xpath(self.adgroup_list)) > 0:
                break
            a = self.driver.wait_presence(self.select_this_campaign).location_once_scrolled_into_view

            if len(self.driver.find_elements_by_xpath(self.adgroup_list)) > 0:
                break

            sleep(0.5)
            self.driver.wait_presence(self.select_this_campaign).click()

            sleep(0.5)
            if len(self.driver.find_elements_by_xpath(self.adgroup_list)) > 0:
                break
            else:
                sleep(0.5)
                count += 1

    def click_close_campaign(self):
        if len(self.driver.find_elements_by_xpath("//material-button[@aria-label='スコープ ナビゲーションのメニューを表示']")) > 0:
            self.driver.find_element_by_xpath("//material-button[@aria-label='スコープ ナビゲーションのメニューを表示']").click()
            sleep(0.5)

        count = 0
        while len(self.driver.find_elements_by_xpath(self.adgroup_list)) > 0 and count <= 3:
            if len(self.driver.find_elements_by_xpath(self.adgroup_list)) == 0:
                break
            a = self.driver.wait_presence(self.select_this_campaign).location_once_scrolled_into_view

            if len(self.driver.find_elements_by_xpath(self.adgroup_list)) == 0:
                break

            sleep(0.5)
            self.driver.wait_presence(self.select_this_campaign).click()

            sleep(0.5)
            if len(self.driver.find_elements_by_xpath(self.adgroup_list)) == 0:
                break
            else:
                sleep(0.5)
                count += 1

    def click_load_more_adgroup(self):
        count = 0
        while count < 4:
            count += 1
            if len(self.driver.find_elements_by_xpath(self.select_this_adgroup)) == 0 and len(
                    self.driver.find_elements_by_xpath(self.load_more_adgroup)) > 0:
                a = self.driver.wait_presence(self.load_more_adgroup).location_once_scrolled_into_view
                sleep(0.5)
                self.driver.wait_presence(self.load_more_adgroup).click()
                sleep(0.5)
            else:
                break

    def click_load_more_campaign(self):
        count = 0
        while count < 4:
            count += 1
            if len(self.driver.find_elements_by_xpath(self.select_this_campaign)) == 0 and len(
                    self.driver.find_elements_by_xpath(self.load_more_campaign)) > 0:
                a = self.driver.wait_presence(self.load_more_campaign).location_once_scrolled_into_view
                sleep(0.5)
                self.driver.wait_presence(self.load_more_campaign).click()
                sleep(0.5)
            else:
                break

    def click_select_adgroup(self):
        a = self.driver.wait_presence(self.select_this_adgroup).location_once_scrolled_into_view
        self.driver.wait_presence(self.select_this_adgroup, 5).click()
        self.driver.wait_presence(self.select_this_adgroup, 5).click()
        sleep(0.5)
        self.driver.wait_presence(self.this_adgroup_selected, 5).click()

    def reselect_asset_tab(self):
        try:
            self.driver.wait_clickable("//div[contains(@class, 'primary-group')]//awsm-skinny-nav-item/a[contains(@navi-id, 'AdAssets-tab')]", 3).click()
        except:
            self.driver.wait_clickable("//div[contains(@class, 'secondary-group')]//awsm-skinny-nav-item/a[contains(@navi-id, 'AdAssets-tab')]", 3).click()

        # "UniversalAppReengagementAdAssets-tab" "UniversalAppAdAssets-tab"

    def check_selected(self):
        check_item = f"//awsm-breadcrumbs[@aria-label='現在の対象範囲は" \
                     f"「すべてのキャンペーン 内の アプリ キャンペーン 内の {self.campaign_name} 内の {self.adgroup_name}」です']"

        self.driver.wait_visible(check_item, 15)

        if f'campaignId={self.campaign_id}' not in self.driver.current_url or \
                f'adGroupId={self.adgroup_id}' not in self.driver.current_url or \
                f'adassets' not in self.driver.current_url:
            raise AssertionError("Link check Error")

    def select_adgroup_by_click_process(self):
        try:
            self.click_load_more_campaign()
            self.click_select_campaign()  # View Adgroup_List
            if len(self.driver.find_elements_by_xpath(self.adgroup_list)) == 0:  # If not Adgroup_List ➡ Error
                return False
            self.click_load_more_adgroup()
            self.click_select_adgroup()
            if len(self.driver.window_handles) > 1:
                raise AssertionError
            self.reselect_asset_tab()
            self.check_selected()
            return True
        except Exception as e:
            print(e)
            self.close_window_tabs()

    def select_adgroup_process(self):
        navigated_by_link = False
        for i in {1, 2}:
            if self.select_adgroup_by_click_process():
                break
        else:
            print("Navigate by link")
            sub_link = f"https://ads.google.com/aw/adassets?ocid={self.ocid}&campaignId={self.campaign_id}&adGroupId={self.adgroup_id}&enableAllBrowsers=1&channel=7" + self.google_sub_link()
            self.driver.get(sub_link)

            navigated_by_link = True
            self.google_table_loading()

            GoogleSideFilter(driver=self.driver, tab="adassets",
                             side_status_dict={'campaign_status': self.side_campaign_status,
                                               'adgroup_status': self.side_adgroup_status},
                             is_account_mark=False).set_side_filter()

        self.google_table_loading()
        self.check_selected()
        return navigated_by_link


class GoogleCloseCampaign(GoogleBase):
    def __init__(self, driver, campaign_name):
        super().__init__(driver)
        self.campaign_name = campaign_name
        self.this_campaign = f"//awsm-campaign-tree//a[contains(@class, 'campaign-item') and @title='{campaign_name}']"
        self.select_this_campaign = f"{self.this_campaign}/material-ripple"
        self.adgroup_list = f"{self.this_campaign}/following-sibling::div[contains(@class, 'ad-group-items')]/a"

    def click_close_campaign(self):
        if len(self.driver.find_elements_by_xpath("//material-button[@aria-label='スコープ ナビゲーションのメニューを表示']")) > 0:
            self.driver.find_element_by_xpath("//material-button[@aria-label='スコープ ナビゲーションのメニューを表示']").click()
            sleep(0.5)

        count = 0
        while len(self.driver.find_elements_by_xpath(self.adgroup_list)) > 0 and count <= 3:
            if len(self.driver.find_elements_by_xpath(self.adgroup_list)) == 0:
                break
            a = self.driver.wait_presence(self.select_this_campaign).location_once_scrolled_into_view

            if len(self.driver.find_elements_by_xpath(self.adgroup_list)) == 0:
                break

            sleep(0.5)
            self.driver.wait_presence(self.select_this_campaign).click()

            sleep(0.5)
            if len(self.driver.find_elements_by_xpath(self.adgroup_list)) == 0:
                break
            else:
                sleep(0.5)
                count += 1
