from app.commons.chrome_driver import Driver
from selenium.webdriver.common.keys import Keys
from time import sleep
import os
from app.downloader.Google.google_loading import GoogleBase
from app.commons.crypt import save_cookies, ck_path, load_cookies


class GoogleLogin(GoogleBase):
    def __init__(self, login_id, login_pw, account_id, link, download_folder_path, keep_open="Close"):
        super().__init__(driver=None)
        self.login_id = login_id
        self.login_pw = login_pw
        self.account_id = account_id
        self.link = link
        self.download_folder_path = download_folder_path
        self.keep_open = keep_open
        if self.login_id == "vu_van_cuong@ca-adv.co.jp":
            self.login_pw = "Vancuong020994"
        self.status = False

    def google_wait_navigated(self, limit_number=4, limit_time=20):
        # wait for page to load
        for tr in range(limit_number):
            counter = 0
            while True:
                counter += 0.5
                sleep(0.5)
                if self.driver.execute_script("return document.readyState") == "complete" or counter > limit_time:
                    break

    def create_driver(self):
        self.driver = Driver()
        self.driver.set_chrome(keep_open=self.keep_open, download_dir=self.download_folder_path)

        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })

    def write_account_id(self):
        login_box = self.driver.wait_visible("//input[@id='identifierId']", 10)
        login_box.clear_and_type(self.login_id + Keys.RETURN)
        sleep(3)

        try:
            self.driver.wait_visible('//*[@id="identifierNext"]', 5).click()
        except:
            pass

        try:
            self.driver.wait_invisible('//*[@id="identifierId"]', 30)
        except:
            pass

    def write_password(self):
        password_box = self.driver.wait_visible("//input[@name='password']", 10)
        password_box.clear_and_type(self.login_pw + Keys.RETURN)
        sleep(0.1)
        try:
            self.driver.wait_visible('//*[@id="passwordNext"]', 5).click()
        except:
            pass

    def write_portal(self):
        p_login_box = self.driver.wait_visible('//input[@id="username_input" and @name="username"]', 20)
        p_password_box = self.driver.wait_visible('//input[@id="password_input"]', 20)
        p_login_box.clear_and_type(self.login_id)
        p_password_box.clear_and_type(self.login_pw + Keys.RETURN)

    def check_logined(self):
        try:
            self.driver.wait_presence(
                f"//div[contains(text(),'{self.account_id}') and contains(@class,'account-info _ngcontent')] | "
                f"//span[contains(text(),'{self.account_id}') and contains(@class,'id _ngcontent')]", 30)
            # load view-loader
            self.driver.wait_visible("//view-loader", 20)
            return True
        except:
            return False

    def locked_check(self):
        if "deniedsigninrejected" in self.driver.current_url and self.driver.execute_script(
                "return document.readyState") == "complete":
            return True
        elif len(self.driver.find_elements_by_xpath("//*[contains(text(),'別のブラウザをお試し')]")) > 0:
            return True
        else:
            return False

    def google_new_login(self):

        for i in range(5):
            sleep(1)
            try:
                """
                1. Login By Cookies of Main, from share folder
                2. Login By Cookies of Main, in local
                4. Login Without Cookies
                5. Login Without Cookies, use random user agent
                """

                if i >= 3:
                    self.create_driver()
                    self.driver.set_page_load_timeout(120)
                    self.driver.get(
                        "https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLogin")
                    sleep(0.1)
                    self.driver.set_page_load_timeout(300)
                else:
                    if i == 0 and self.login_id == "vu_van_cuong@ca-adv.co.jp":
                        cookies = load_cookies(
                            os.path.join(r'\\vnd\share\02_共有資料\[RPA_他]\Navigator', f"Google_{self.login_id}.txt"))
                    elif i == 1:
                        continue
                    elif i == 2:
                        cookies = load_cookies(ck_path("Google", self.login_id))
                    else:
                        continue

                    if cookies is None:
                        continue

                    self.create_driver()

                    self.driver.get("https://ads.google.com/")
                    for cookie in cookies:
                        for ckinf in ['sameSite', 'expiry']:
                            try:
                                del cookie[ckinf]
                            except:
                                pass
                        self.driver.add_cookie(cookie)

                    self.driver.get(self.link + "&enableAllBrowsers=1")

                # 3 times
                for s in range(3):
                    try:
                        self.google_wait_navigated()
                        if 'multifactorauthalert' in self.driver.current_url:
                            raise ValueError
                        self.driver.wait_presence("//input[@id='identifierId'] | "
                                                  "//input[@name='password'] | "
                                                  "//*[@id='username_input'] | "
                                                  f"//*[contains(@aria-label, '{self.login_id}')] | "
                                                  f"//*[contains(@class, 'email') and text()='{self.login_id}']")

                        if self.driver.get_elements("//input[@id='identifierId']").count > 0:
                            self.write_account_id()
                        elif self.driver.get_elements("//*[@id='username_input']").count > 0:
                            self.write_portal()
                        elif self.driver.get_elements("//*[@id='username_input']").count > 0:
                            self.write_password()
                        else:
                            break
                        self.google_wait_navigated()
                    except:
                        if "usernamerecovery" in self.driver.current_url:
                            self.driver.get(
                                "https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLogin")
                            sleep(1)
                            self.google_wait_navigated()
                        elif 'multifactorauthalert' in self.driver.current_url:
                            dictss = {}
                            for item in ['euid', '__u', 'uscid', '__c', 'authuser']:
                                if item + '=' in self.driver.current_url:
                                    val = str(self.driver.current_url).split(item + '=')[1].split("&")[0]
                                    dictss[item] = val
                            for key, val in dictss.items():
                                self.link = self.link + "&" + key + "=" + val
                            self.driver.get(self.link + "&enableAllBrowsers=1")
                            sleep(1)
                            self.google_wait_navigated()
                        elif self.locked_check():
                            raise ValueError
                        elif "myaccount.google" in self.driver.current_url:
                            break

                if len(self.driver.find_elements_by_xpath(
                        f"//*[contains(@class, 'email') and text()='{self.login_id}']")) == 0:
                    count = 0
                    while True:
                        sleep(1)
                        count += 1
                        if ("myaccount.google" in self.driver.current_url and self.driver.execute_script(
                                "return document.readyState") == "complete") or count > 15:
                            break

                if 'login' in self.driver.current_url:
                    raise AssertionError()

                if i >= 3:
                    self.driver.get(self.link + "&enableAllBrowsers=1")
                    sleep(0.5)

                curl = self.driver.current_url
                if 'multifactorauthalert' in curl:
                    dictss = {}
                    for item in ['euid', '__u', 'uscid', '__c', 'authuser']:
                        if item + '=' in curl:
                            val = str(curl).split(item + '=')[1].split("&")[0]
                            dictss[item] = val

                    for key, val in dictss.items():
                        self.link = self.link + "&" + key + "=" + val
                    self.driver.get(self.link + "&enableAllBrowsers=1")
                    sleep(1)

                if 'cookiemismatch' in curl.lower():
                    try:
                        file = ck_path("Google", self.login_id)
                        os.unlink(file)
                    except:
                        pass

                    raise ValueError()

                if self.check_logined():
                    self.status = True

            except Exception as e:
                print(e)
                try:
                    self.driver.quit()
                except:
                    pass

            finally:
                if self.status:
                    break

    def login_process(self):
        self.google_new_login()
        if not self.status or self.status == 'Locked':
            return None
        else:
            try:
                save_cookies(self.driver, ck_path("Google", self.login_id))
            except:
                pass
            print('Login OK')
        return self.driver
