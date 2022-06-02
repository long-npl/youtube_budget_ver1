from app.commons.chrome_driver import Driver
from time import sleep


class GoogleBase:
    def __init__(self, driver: Driver = None):
        self.driver = driver

    def google_table_loading(self):
        sleep(0.5)

        try:
            self.driver.wait_invisible("//*[contains(@class, 'particle-content-loading'))]", 50)
        except:
            pass

        try:
            self.driver.wait_invisible("//ipl-progress-indicator", 50)
        except:
            pass

        try:
            self.driver.wait_presence("//progress-indicator", 50)
        except:
            pass

        try:
            if 'reporting/reporteditor/view' not in self.driver.current_url:
                load = "//*[contains(@aria-label, 'の表') and not(contains(@class, 'loading')) and contains(@class, 'particle-table')]"
                self.driver.wait_presence(load, 60)
            else:
                load = "//matcha-table//*[not(contains(@class, 'loading')) and contains(@class, 'ess-table-canvas')]"
                un_load = "//*[contains(@class, 'interaction-disabled')]"
                self.driver.wait_presence(load, 60)
                self.driver.wait_invisible(un_load, 60)
        except:
            pass

    def google_sub_link(self):
        curl = self.driver.current_url
        pars = {}
        for item in ['euid', '__u', 'uscid', '__c', 'authuser']:
            if item + '=' in curl:
                val = str(curl).split(item + '=')[1].split("&")[0]
                pars[item] = val

        sub_link = ""
        for key, val in pars.items():
            sub_link += f"&{key}={val}"

        return sub_link
