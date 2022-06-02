from time import sleep
from app.downloader.Google.google_loading import GoogleBase

en_fils = {'削除済みを除くすべて': 'All but removed',
           '有効のみ': 'All enabled',
           'すべて': 'All'}

new_fils = {'削除済みを除くすべて': '有効、一時停止',
            '有効のみ': '有効',
            'すべて': 'すべて'}

compare_signs = [" > ", " >= ", " = ", " <= ", " < ", " 等しくない ",
                 " 次を含む ", ' 次を含まない ', " 次を含む（大文字と小文字を区別） ",
                 " 次を含まない（大文字と小文字を区別） ", " 等しい ", ' 次から始まる ']

include_signs = [' いずれかを含む ', ' すべてを含む ', ' いずれも含まない ', ": "]


def get_fil(fil, array):
    for sign in array:
        if sign in fil:
            return sign
    else:
        return None


class GoogleFullFilter(GoogleBase):

    setting_button = "//awsm-left-nav-settings[@navi-id='left-nav-settings-button']"

    def __init__(self, driver, tab, view, main_filter, side_status_dict, is_account_mark=False):
        super().__init__(driver)
        self.tab = tab
        self.view = view
        self.main_filter = main_filter
        self.side_status_dict = side_status_dict
        self.is_account_mark = is_account_mark

    def set_view(self):
        if 'demographics' in self.tab:
            button = "//toolbelt//*[text()='広告グループ表示' or text() = 'キャンペーン表示' or text() = 'アカウントの概要']/ancestor::material-button"
            view = '広告グループ表示' if self.view == "" else self.view
        elif self.tab == 'adextensions':
            button = "//toolbelt//*[text()='広告表示オプション ビュー' or text() = '関連付けビュー']/ancestor::dropdown-button"
            view = '広告表示オプション ビュー' if self.view == "" else self.view
        elif self.tab == 'locations':
            button = "//toolbelt//*[text()='ターゲット地域' or text() = '一致した地域（キャンペーン）' or text()='一致した地域（アカウント）']/ancestor::material-button"
            view = '一致した地域（キャンペーン）' if self.view == "" else self.view

            if ' | 都道府県' in view:
                view = view.replace(' | 都道府県', "")
        else:
            return True

        print(self.view)
        self.driver.wait_presence(button).click()
        sleep(1)
        self.driver.wait_presence(f"//div//material-select-item[@aria-label='{view}']").click()
        self.google_table_loading()

        self.driver.wait_presence(f"//toolbelt//*[text()='{view}']")

        print("VIEW OK")

    def set_auction_view(self):
        if (self.tab in ['campaigns', 'adgroups', 'keywords'] and self.view == 'オークション分析') or (
                self.tab == "locations" and "都道府県" in self.view):
            """
            selected_text = self.driver.wait_presence("//pagination-bar//*[contains(@class, 'selected')]"
                                                      "//div[contains(@aria-label, 'おおよそ全')]").get_attribute(
                "aria-label")
            max_item = int(selected_text.split("（おおよそ全 ")[-1].split("行")[0].strip())"""

            selected_text = self.driver.wait_presence("//pagination-bar//*[contains(@class, 'selected')]"
                                                      "//div[contains(text(), ' 件中 ') and contains(text(), ' 件を表示')]").text

            max_item = int(selected_text.split(" 件中")[0].strip())

            print(max_item)

            if max_item > 500:
                raise ValueError(f"オークションアイテムが多い（500行以上）ので選択できない: {max_item}")

            "841 件中 1～500 件を表示"
            fr, tr = selected_text.split(" 件中 ")[-1].replace(" 件を表示", "").split("～")
            this_item = int(tr.strip()) - int(fr.strip()) + 1
            if this_item < max_item:
                xxx = self.driver.wait_presence("//pagination-bar").location_once_scrolled_into_view
                self.driver.find_element_by_xpath("//pagination-bar//*[contains(text(), '表示する行')]"
                                                  "//following-sibling::material-dropdown-select"
                                                  "//dropdown-button").click()
                sleep(0.5)
                a = self.driver.wait_presence(
                    "//material-list//material-select-dropdown-item[@role='option']//*[text()='500']")
                sleep(0.5)
                a.click()

            self.driver.wait_clickable("//view-loader//header-tools-cell"
                                       "//mat-checkbox[@aria-label='すべての行を選択します' and @aria-checked='false']",
                                       10).click()
            sleep(0.5)
            self.google_table_loading()

            sleep(1)
            self.driver.wait_invisible("//tableview//toolbelt-bar//*[contains(@class, 'select-across-pages-link')]", 10)

            check_text = self.driver.wait_presence("//tableview//section//toolbelt-bar//selection").text
            if max_item == 1:
                final_text = "1 行選択済み"
            else:
                final_text = f"全 {max_item} 行選択済み"

            if str(check_text) != final_text:
                raise ValueError(f"フィルターできたすべての行が選択されていない: {check_text}, 正しい:　{final_text}")

            if self.tab == "locations":
                print("Location View")
                self.driver.wait_visible(
                    "//tableview//toolbelt-bar//*[text()='条件指定:']/ancestor::material-button").click()
                self.driver.wait_visible("//menu-item-groups//material-select-item[@aria-label='都道府県']").click()
                self.driver.wait_presence("//dynamic-component//dropdown-button//*[text()='都道府県']")

            else:
                self.driver.wait_visible(
                    "//tableview//toolbelt-bar//*[text()='オークション分析']/parent::material-button").click()
                sleep(1)

                if '/auctioninsights' not in self.driver.current_url:
                    raise AssertionError("オークション分析ページに移動失敗しました。")

    def set_total_filter(self):
        GoogleSideFilter(self.driver, self.tab, self.side_status_dict, self.is_account_mark).set_side_filter()
        GoogleMainFilter(self.driver, self.main_filter).set_main_filter()
        self.set_view()
        self.set_auction_view()


class GoogleSideFilter(GoogleBase):
    setting_button = "//awsm-left-nav-settings[@navi-id='left-nav-settings-button']"

    def __init__(self, driver, tab, side_status_dict, is_account_mark=False):
        super().__init__(driver)
        self.tab = tab
        self.side_status_dict = side_status_dict
        self.is_account_mark = is_account_mark

    def unhide_side_tab(self):
        if len(self.driver.get_elements("//*[@navi-id='app-bar-primary-action-button']")) > 0:
            if len(self.driver.get_elements("//material-button[@aria-label='スコープ ナビゲーションのメニューを非表示']")) > 0:
                pass
            else:
                self.driver.get_element("//awsm-left-nav/material-button[@aria-label='スコープ ナビゲーションのメニューを表示']").click()

    def select_side_status(self, side_tab, side_status):
        side_tab = 'ad-group' if side_tab == "adgroup" else side_tab
        set_status = f"//material-select[contains(@class,'{side_tab}-filter-mode')]" \
                     f"//material-select-item/span[text()='{side_status}' or text()='{en_fils[side_status]}']"

        selected = f"//material-select[contains(@class, 'material-select {side_tab}-filter-mode')]//" \
                   f"material-select-item//*[text()='{side_status}' or text()='{en_fils[side_status]}']//ancestor::material-select-item"

        for retry in range(4):
            self.unhide_side_tab()
            self.driver.wait_visible(self.setting_button, 30).click()
            sleep(1)
            # Select campaign status
            self.driver.wait_visible(set_status, 30).click()
            sleep(2)
            self.google_table_loading()
            selected_aria = self.driver.wait_presence(selected, 30).get_attribute("class")
            if "selected" in selected_aria:
                break
        else:
            raise AssertionError(f"{side_tab}のステータスを選択失敗しました")

        sleep(0.5)
        self.google_table_loading()

    def check_and_set_side_status(self, side_tab, side_status):
        side_tab = 'ad-group' if side_tab == "adgroup" else side_tab
        set_status = f"//material-select[contains(@class,'{side_tab}-filter-mode')]" \
                     f"//material-select-item/span[text()='{side_status}' or text()='{en_fils[side_status]}']"

        selected = f"//material-select[contains(@class, 'material-select {side_tab}-filter-mode')]//" \
                   f"material-select-item//*[text()='{side_status}' or text()='{en_fils[side_status]}']//ancestor::material-select-item"

        selected_aria = self.driver.wait_presence(selected, 30).get_attribute("class")
        if "selected" in selected_aria:
            pass
        else:
            for retry in range(4):
                self.unhide_side_tab()
                sleep(0.5)
                a = self.driver.wait_presence(self.setting_button).location_once_scrolled_into_view
                self.driver.wait_presence(self.setting_button, 30).click()
                sleep(1)
                # Select campaign status
                self.driver.wait_visible(set_status, 30).click()
                sleep(2)
                self.google_table_loading()
                selected_aria = self.driver.wait_presence(selected, 30).get_attribute("class")
                if "selected" in selected_aria:
                    break
            else:
                raise AssertionError(f"{side_tab}のステータスを選択失敗しました")
        sleep(0.5)
        self.google_table_loading()

    def set_account_mark_filter(self):
        # In case of # アカウント採点のデータ準備
        for ret in range(6):

            if len(self.driver.find_elements_by_xpath("//aw-header-cell[text()='目標コンバージョン単価']")) > 0:
                break
            sleep(2)

            self.driver.wait_presence(
                "//awsm-left-nav//awsm-channel-picker//div[text()='すべてのキャンペーン']//ancestor::div[contains(@class, 'list-picker-item ')]").click()
            self.google_table_loading()
            sleep(0.5)
            self.driver.wait_presence(
                "//awsm-left-nav//awsm-channel-picker//div[text()='ディスプレイ キャンペーン']//ancestor::div[contains(@class, 'list-picker-item ')]").click()
            self.google_table_loading()
            sleep(0.5)

            assert "channel=2" in self.driver.current_url, "Reselect Error"

        else:
            print("目標コンバージョン単価 not found")
            raise ValueError("目標コンバージョン単価 not found")

    def set_side_filter(self):
        # In case of # アカウント採点のデータ準備
        if self.is_account_mark:
            self.set_account_mark_filter()

        print("Set Side")
        if self.tab == 'campaigns':
            status_set = []
        elif self.tab in ['adgroups', 'campaigns/auctioninsights']:
            status_set = ['campaign']
        else:
            status_set = ['campaign', 'adgroup']

        for side_tab in status_set:
            print(side_tab, self.side_status_dict[f"{side_tab}_status"])
            self.select_side_status(side_tab, self.side_status_dict[f"{side_tab}_status"])


class GoogleMainFilter(GoogleBase):

    filter_add = "//inline-filter-bar//input[@aria-label='フィルタを追加'] | " \
                 "//inline-filter-bar//material-button[@aria-label='フィルタを追加']"

    def __init__(self, driver, main_filter):
        super().__init__(driver)
        self.main_filter = main_filter

    def set_main_filter(self, check_texts=None, force_reset=False):
        self.close_filter_panel()

        ggft = GoogleFilterText(self.driver)  # Filter Text 起動
        # Set Main Filter
        if check_texts is None:
            check_texts = PossibleFilters().collect(self.main_filter)

        filters = self.main_filter.split("; ")

        if not force_reset:  # IF FORCE_RESET, SKIP
            filter_text = ggft.get_filter_text()
            if filter_text in check_texts:
                return True

        self.reset_main_filter()
        for fil in filters:
            if 'のステータス: ' in fil or fil.startswith('ネットワーク: ') or fil.startswith('広告表示オプションの種類: '):
                component, component_status = fil.split(": ")
                en_com = new_fils.get(component_status, component_status)

                a = f"//span[contains(@class,'predicate-lead') and contains(text(),'{component}')]"
                b = f"//filter-bar//material-chip | //filter-bar//*[contains(@class, 'filter-count')]"
                self.driver.wait_presence(f"{a} | {b}")

                if len(self.driver.find_elements_by_xpath(a)) > 0:
                    print("OLD FILTER")

                    self.driver.wait_visible(f"//*[contains(@class,'predicate-lead') and contains(text(),'{component}')]", 5).click()
                    sleep(1)

                    select_component_status = f"//div[@pane-id]//filter-editor-dropdown" \
                                              f"//material-select-item[text()='{component_status}' or text()='{en_com}']"

                    wrong_select = f"//focus-trap//material-list[@aria-label='フィルタを追加']"
                    self.driver.wait_presence(f"{select_component_status} | {wrong_select}")
                    if len(self.driver.get_elements(wrong_select)) > 0:
                        self.driver.wait_clickable("//filter-bar").click()
                        self.driver.wait_visible(f"//filter-bar//div[contains(text(),'{component}')]//ancestor::predicate-editor",5).click()

                    sleep(1)
                else:
                    self.driver.wait_clickable("//filter-bar").click()
                    sleep(1)
                    select_component_status = f"//div[@pane-id]//filter-editor-dropdown" \
                                              f"//material-select-item[text()='{en_com}' or text()='{component_status}']"

                    sleep(1)
                self.driver.wait_presence(select_component_status).click()
                sleep(0.5)
                self.close_filter_panel()
            elif (compare_sign := get_fil(fil, compare_signs)) is not None:
                self.set_compare_filter(fil, compare_sign)
            elif (include_sign := get_fil(fil, include_signs)) is not None:
                self.set_include_filter(fil, include_sign)
            elif fil == "":
                pass
            else:
                raise ValueError(f"Invalid Filter: {fil}")

            self.google_table_loading()
            sleep(0.5)

            if len(self.driver.get_elements("//input[@aria-expanded='true' and @aria-label='フィルタを追加']")) > 0:
                self.driver.get_element("//input[@aria-expanded='true' and @aria-label='フィルタを追加']").click()
                sleep(0.5)

            self.close_filter_panel()

        self.google_table_loading()
        sleep(0.5)

        if len(self.driver.get_elements("//input[@aria-expanded='true' and @aria-label='フィルタを追加']")) > 0:
            self.driver.get_element("//input[@aria-expanded='true' and @aria-label='フィルタを追加']").click()
            sleep(0.5)

        self.close_filter_panel()

        sleep(0.5)

        filter_text = ggft.get_filter_text()
        if len(str(check_texts[0]).split(';')[2].split('、')) >= 3:
            check_texts = str(check_texts[0]).split(';')[0] + ';' + str(check_texts[0]).split(';')[1].replace(' > ', ': >: ')\
                          + ';' + str(check_texts[0]).split(';')[2].split('、')[0] + '、' + \
                          str(check_texts[0]).split(';')[2].split('、')[1] + '（その他 1 個）'
        print(check_texts)
        if filter_text not in check_texts:
            raise AssertionError(
                "Select Filter Failed.\nExpected: {}.Selected Filter: {}".format(check_texts, filter_text))

    def set_main_filter_proc(self, check_texts=None, force_reset=False):
        try:
            self.set_main_filter(check_texts, force_reset)
        except Exception as e:
            print("Filter ERROR", e)
            raise ValueError

    def set_compare_filter(self, fil, compare_sign):
        compare_col, compare_value = fil.split(compare_sign)

        compare_value = compare_value.replace(chr(165), "").replace("%", "").replace(r"￥", "").strip()
        compare_col = compare_col.rstrip(":")

        self.driver.wait_visible(self.filter_add).click()
        search_box = "//div[@pane-id]//input[@aria-label='フィルタを追加' and contains(@class,'search-box popup')]"
        self.driver.wait_visible(search_box).clear_and_type(compare_col)

        col_select = f"//div[@pane-id]//material-list//material-select-item[@aria-label='{compare_col}'] | " \
                     f"//div[@pane-id]//material-list//material-select-dropdown-item[@aria-label='{compare_col}']"
        self.driver.wait_visible(col_select).click()
        sleep(0.5)

        self.driver.wait_visible("//div[@pane-id]//focus-trap//predicate-operator//dropdown-button"
                                 "//i[text()='arrow_drop_down']/ancestor::div[@role='button']").click()
        sleep(0.5)

        compare_element = f"//div[@pane-id]//material-list-item[text()='{compare_sign.strip()}'] | " \
                          f"//div[@pane-id]//material-select-dropdown-item//*[text()='{compare_sign.strip()}']"

        self.driver.wait_visible(compare_element).click()

        compre_num_box = "//div[@pane-id]//filter-editor-percent//material-input//input | " \
                         "//div[@pane-id]//filter-editor-number//material-input//input | " \
                         "//div[@pane-id]//filter-editor-money//material-input//input | " \
                         "//div[@pane-id]//filter-editor-string//material-input//input | " \
                         "//div[@pane-id]//filter-editor-percent//material-input//textarea | " \
                         "//div[@pane-id]//filter-editor-number//material-input//textarea | " \
                         "//div[@pane-id]//filter-editor-money//material-input//textarea | " \
                         "//div[@pane-id]//filter-editor-string//material-input//textarea"

        sleep(0.5)
        self.driver.wait_visible(compre_num_box).send_keys(compare_value)
        ok_box = "//div[@pane-id]//focus-trap//material-button[@aria-label='適用']"
        self.driver.wait_visible(ok_box).click()
        sleep(0.3)

    def set_include_filter(self, fil, include_sign):
        select_col, select_vals = fil.split(include_sign)
        select_col = select_col.rstrip(":")

        self.driver.wait_visible(self.filter_add).click()
        search_box = "//div[@pane-id]//input[@aria-label='フィルタを追加' and contains(@class,'search-box popup')]"
        select_col_xpath = f"//div[@pane-id]//material-list//material-select-item[@aria-label='{select_col}']"

        self.driver.wait_visible(search_box).clear_and_type(select_col)
        self.driver.wait_visible(select_col_xpath).click()
        sleep(1)

        if include_sign != ": ":
            self.driver.wait_visible("//div[@pane-id]//focus-trap//predicate-operator//dropdown-button"
                                     "//i[text()='arrow_drop_down']/ancestor::div[@role='button']").click()
            sleep(0.5)

            include_element = f"//div[@pane-id]//material-list-item[text()='{include_sign.strip()}'] | " \
                              f"//div[@pane-id]//material-select-dropdown-item//*[text()='{include_sign.strip()}']"
            self.driver.wait_visible(include_element).click()

        # Load more
        try:
            count = 0
            while len(self.driver.get_elements(
                    "//ess-picker-section//div[contains(@class, 'load-more-container')]//material-button")) > 0 and count < 20:
                count += 1
                self.driver.wait_clickable(
                    "//ess-picker-section//div[contains(@class, 'load-more-container')]//material-button").click()
                sleep(0.5)
        except:
            pass

        # Uncheck
        for selected_row in self.driver.get_elements(
                "//ess-particle-table//div[@role='row' and contains(@class, 'selected')]//mat-checkbox | "
                "//ess-particle-table//div[@role='row' and contains(@class, 'selected')]//material-checkbox"):
            selected_row.click()

        for select_val in select_vals.split("、"):
            picker_search = "//div[@pane-id]//focus-trap//picker-search-box//material-input//input"
            if len(self.driver.get_elements(picker_search)) > 0:
                try:
                    self.driver.wait_visible(picker_search).clear_and_type(select_val)
                except:
                    pass

            select_e_cpn = f"//div[@pane-id]//filter-editor-picker//campaign-name-cell/div[text()='{select_val}']" \
                           f"/ancestor::div[@role='row']//tools-cell//mat-checkbox[@aria-disabled='false']"
            select_e_adg = f"//div[@pane-id]//filter-editor-picker//text-field[text()='{select_val}']" \
                           f"/ancestor::div[@role='row']//tools-cell//mat-checkbox[@aria-disabled='false']"
            select_e_other = f"//div[@pane-id]//filter-editor-list//material-checkbox[@aria-checked='false']" \
                             f"//div[text()='{select_val}']"
            select_e_label = f"//div[@pane-id]//label-filter-editor-picker//filter-label//*[text()='{select_val}']" \
                             f"//ancestor::ess-cell/preceding-sibling::colored-checkbox-tools-cell" \
                             f"//mat-checkbox[not(@checked)]"

            select_e = select_e_cpn + " | " + select_e_adg + " | " + select_e_other + " | " + select_e_label

            if self.driver.wait_clickable(select_e):
                self.driver.wait_clickable(select_e).click()

        self.driver.wait_visible("//div[@pane-id and contains(@class, 'filter-editor-picker')]"
                                 "//focus-trap//div[text()='適用']/parent::material-button").click()

    def reset_main_filter(self):
        # Filter Reset
        # self.driver.wait_clickable("//filter-bar//material-icon[contains(@class, 'filter-icon')] | //filter-bar || //inline-filter-bar", 60).click()
        self.driver.wait_clickable(self.filter_add, 60).click()
        try:
            self.driver.wait_visible("//material-button[contains(@aria-label,'フィルタをデフォルトの状態にリセット')]", 3).click()
            sleep(0.5)
        except:
            self.driver.wait_clickable("//filter-bar//material-icon[contains(@class, 'filter-icon')] | //filter-bar", 10).click()

        self.google_table_loading()
        self.close_filter_panel()

    def close_filter_panel(self):
        if len(self.driver.get_elements("//material-button[contains(@aria-label,'フィルタパネルを閉じ')]")) > 0:
            self.driver.get_element("//material-button[contains(@aria-label,'フィルタパネルを閉じ')]").click()
            sleep(0.5)


class GoogleFilterText(GoogleBase):
    def __init__(self, driver):
        super().__init__(driver)

    def visible_and_get_filter(self, button_text):
        self.driver.find_element_by_xpath(f"//inline-filter-bar//*[text()='{button_text}' and contains(@class, 'view-all-label')]").click()
        filter_text = self.driver.wait_visible("//div[contains(@class, 'popup-predicate-container')]", 6).text

        if filter_text.startswith("フィルタ"):
            filter_text = filter_text[5:].replace(chr(10), "; ")
        else:
            filter_text = filter_text.replace(chr(10), "; ")

        sleep(0.3)

        self.driver.wait_visible("//*[@pane-id]//*[contains(@class, 'popup') and contains(@class, ' visible')]"
                                 "//material-button[contains(@class, 'close-popup-btn')]", 7).click()

        return filter_text

    def get_filter_text(self):

        self.google_table_loading()  # Wait Loading

        filter_text = self.driver.wait_visible("//inline-filter-bar", 30).text

        all_filters = filter_text.split(chr(10))

        if all_filters[-1] != "フィルタを追加" or all_filters[0] != "filter_alt":
            raise ValueError(f"invalid structure of filter bar, all_filters {all_filters}")
        del all_filters[-1]
        del all_filters[0]

        if "すべて表示" in all_filters:
            filter_text = self.visible_and_get_filter("すべて表示")
        else:
            if len(all_filters) > 0:
                filter_count_e = "//filter-bar//div[contains(@class, 'filter-count')]"
                if len(self.driver.find_elements_by_xpath(filter_count_e)) > 0:
                    filter_count = self.driver.wait_visible(filter_count_e).text
                    assert all_filters[0] == filter_count, f"invalid structure of filter bar, all_filters {all_filters}, filter_count: {filter_count}"
                    del all_filters[0]

            if len(all_filters) == 0:
                filter_text = ""
            else:
                last_ele = all_filters[-1]
                if last_ele.startswith("他") and last_ele.endswith("個") or last_ele.startswith("+") and last_ele.endswith("more"):
                    add_text = self.visible_and_get_filter(last_ele)
                    filter_text = "; ".join(all_filters[:-1]) + "; " + add_text
                else:
                    filter_text = "; ".join(all_filters)
        print(filter_text)
        return filter_text


class PossibleFilters:

    @staticmethod
    def collect(main_filter):
        print("Collect Possible Filter Texts")
        if main_filter == "":
            return ['']
        all_filters = main_filter.split("; ")
        all_possible = []

        for fil in all_filters:
            filters_to_add = []
            if 'のステータス: ' in fil or fil.startswith('ネットワーク: ') or fil.startswith('広告表示オプションの種類: '):
                component, component_status = fil.split(": ")
                filters_to_add.append(f"{component}:: {component_status}")
                filters_to_add.append(f"{component}: {component_status}")
                if component_status in new_fils:
                    filters_to_add.append(f"{component}:: {new_fils[component_status]}")
                    filters_to_add.append(f"{component}: {new_fils[component_status]}")
            elif (compare_sign := get_fil(fil, [*compare_signs, *include_signs])) is not None:
                compare_col, compare_value = fil.split(compare_sign)
                filters_to_add.append(f"{compare_col}{compare_sign}{compare_value}")
                filters_to_add.append(f"{compare_col}{compare_sign.rstrip()}: {compare_value}")
                filters_to_add.append(f"{compare_col}:{compare_sign}{compare_value}")
                filters_to_add.append(f"{compare_col}:{compare_sign.rstrip()}: {compare_value}")
            elif fil == "":
                pass
            else:
                raise ValueError(f"Invalid Filter: {fil}")

            if len(filters_to_add) > 0:
                if len(all_possible) == 0:
                    new_possible = filters_to_add
                else:
                    new_possible = []
                    for idx, seng in enumerate(all_possible):
                        for to_add in filters_to_add:
                            new_possible.append(f"{seng}; {to_add}")
                all_possible = new_possible
        return all_possible





