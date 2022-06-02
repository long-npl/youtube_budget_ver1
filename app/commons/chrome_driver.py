from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
import selenium.webdriver.support.expected_conditions as EC

import os
import sys
from time import sleep
import subprocess
import winreg
import xml.etree.ElementTree as elemTree
import requests
from zipfile import ZipFile
from io import BytesIO
import functools
from contextlib import suppress
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'my.packg': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        '__main__': {  # if __name__ == '__main__'
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

LOCAL_FOLDER = os.path.abspath(os.path.dirname(sys.argv[0]))
TRIED = False

__all__ = ['Driver', "CHROME"]

CHROME = webdriver.Chrome


def get_chrome_installed(hive, flag):
    try:
        a_reg = winreg.ConnectRegistry(None, hive)
        a_key = winreg.OpenKey(a_reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_READ | flag)
        a_sub = winreg.OpenKey(a_key, "Google Chrome")
        return winreg.QueryValueEx(a_sub, "DisplayVersion")[0]
    except:
        pass


def get_web_chrome_link(version):
    logger.info("Try to get target chrome driver in web")

    res = requests.get("https://chromedriver.storage.googleapis.com")
    root = elemTree.fromstring(res.content)
    for k in root.iter('{http://doc.s3.amazonaws.com/2006-03-01}Key'):
        if k.text.find(version + '.') == 0:
            ver = k.text.split('/')[0]
            logger.info(f"found web_version: {ver}")
            return ver
    logger.warning(f"not found matched version of chrome: {version}")


def download_web_chrome(version, chrome_driver):
    web_version = get_web_chrome_link(version)

    logger.info(f"Try to download from web: {web_version}")
    link = f"https://chromedriver.storage.googleapis.com/{web_version}/chromedriver_win32.zip"
    res = requests.get(link)
    with ZipFile(BytesIO(res.content)) as zip_file:
        for info in zip_file.infolist():
            if info.filename == "chromedriver.exe":
                info.filename = chrome_driver

                zip_file.extract(info, LOCAL_FOLDER)
                return


def get_chrome_version():
    chrome_driver = 'chromedriver.exe'
    version = ""
    try:
        if os.path.exists("C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"):
            output = subprocess.check_output(
                r'wmic datafile where name="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" '
                r'get Version /value', shell=True)
        else:
            output = subprocess.check_output(
                r'wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" '
                r'get Version /value', shell=True)

        version = output.decode('utf-8').strip().split("=")[1].split(".")[0]

        chrome_driver = f'chromedriver_{version}.exe'
    except:
        for hive, flag in ((winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY),
                           (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
                           (winreg.HKEY_CURRENT_USER, 0)):
            cr_ver = get_chrome_installed(hive, flag)
            if cr_ver is not None:
                version = str(cr_ver).split(".")[0]
                chrome_driver = f'chromedriver_{version}.exe'
                break

    global TRIED
    if version != "" and not TRIED and not os.path.exists(os.path.join(LOCAL_FOLDER, chrome_driver)):
        try:
            download_web_chrome(version, chrome_driver)
        finally:
            TRIED = True

    logger.info(f"found version: {chrome_driver}")

    return chrome_driver


CHROME_VERSION = get_chrome_version()


def selenium_error(func):
    @functools.wraps(func)
    def xpath_wrapper(self, xpath, *args, **kwargs):
        try:
            value = func(self, xpath, *args, **kwargs)
        except WebDriverException as e:
            e.msg = getattr(e, "msg", "") + f"{func.__name__}, xpath: {xpath}"       # Update xpath to message
            raise
        return value
    return xpath_wrapper


class Driver:
    _default_wait_time = 30

    def __init__(self, driver_: webdriver.Chrome = None):
        self.driver_ = driver_

    def __getattr__(self, attr):
        return getattr(self.driver_, attr)

    def __del__(self):
        if self.driver_ is not None:
            with suppress(Exception):
                self.driver_.quit()

    def set_chrome(self, keep_open="Close", download_dir=None, load_cookies=False, proxy=""):
        chrome_options = webdriver.ChromeOptions()

        if download_dir is not None:
            prefs = {"download.default_directory": os.path.abspath(download_dir)}
            chrome_options.add_experimental_option("prefs", prefs)

        if "Keep_Open" in keep_open:
            chrome_options.add_experimental_option("detach", True)
        else:
            chrome_options.add_experimental_option("detach", False)
            if "headless" in keep_open:
                chrome_options.headless = True

        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')

        if ":" in str(proxy):
            chrome_options.add_argument('--proxy-server=http://{}'.format(proxy))

        chrome_options.add_experimental_option("excludeSwitches",
                                               ["ignore-certificate-errors",
                                                "safebrowsing-disable-download-protection",
                                                "safebrowsing-disable-auto-update",
                                                "disable-client-side-phishing-detection",
                                                'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        if load_cookies:
            dirs = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Google\\Chrome\\User Data"
            chrome_options.add_argument("--user-data-dir=" + dirs)

        else:
            chrome_options.add_argument("--incognito")

        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--disable-logging')

        self.driver_ = webdriver.Chrome(executable_path=os.path.join(LOCAL_FOLDER, CHROME_VERSION), options=chrome_options)

    def wait(self, wait_time=_default_wait_time):
        return WebDriverWait(self.driver_, wait_time)

    @selenium_error
    def wait_presence(self, xpath, wait_time=_default_wait_time):
        return Element(self.wait(wait_time).until(EC.presence_of_element_located((By.XPATH, xpath))))

    @selenium_error
    def wait_visible(self, xpath, wait_time=_default_wait_time):
        return Element(self.wait(wait_time).until(EC.visibility_of_element_located((By.XPATH, xpath))))

    @selenium_error
    def wait_invisible(self, xpath, wait_time=_default_wait_time):
        return Element(self.wait(wait_time).until(EC.invisibility_of_element_located((By.XPATH, xpath))))

    @selenium_error
    def wait_clickable(self, xpath, wait_time=_default_wait_time):
        return Element(self.wait(wait_time).until(EC.element_to_be_clickable((By.XPATH, xpath))))

    def get_element(self, xpath):
        return Element(self.driver_.find_element(by=By.XPATH, value=xpath))

    def get_elements(self, xpath):
        return [Element(item) for item in self.driver_.find_elements(by=By.XPATH, value=xpath)]

    def set_session_storage(self, key, value):
        self.driver_.execute_script("return window.sessionStorage.setItem(arguments[0], arguments[1]);", key, value)

    def set_local_storage(self, key, value):
        self.driver_.execute_script("return window.localStorage.setItem(arguments[0], arguments[1]);", key, value)

    def remove_local_storage(self, key):
        self.set_local_storage(key, "")
        self.driver_.execute_script("return window.localStorage.removeItem(arguments[0]);", key)

    def get_session_storage(self, key):
        return self.driver_.execute_script("return window.sessionStorage.getItem(arguments[0]);", key)

    def get_local_storage(self, key):
        return self.driver_.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    def get_local_storage_keys(self):
        return self.driver_.execute_script("return Object.keys(window.localStorage);")

    def get_cookies_string(self):
        cookies = self.driver_.get_cookies()
        cookies_string = '; '.join(['{}={}'.format(cookie['name'], cookie['value']) for cookie in cookies])
        return cookies_string

    def get_user_agent(self):
        return self.driver_.execute_script("return navigator.userAgent;")

    @property
    def user_agent(self):
        return self.driver_.execute_script("return navigator.userAgent;")


class Element:
    def __init__(self, element):
        self.ele = element

    def __getattr__(self, attr: str):
        return getattr(self.ele, attr)

    def get_text(self):
        return self.ele.text

    def clear_and_type(self, content: str):
        self.clear()
        sleep(0.5)
        self.send_keys(content)

    def select_value(self, value):
        Select(self.ele).select_by_value(value)

    def select_visible_text(self, text):
        Select(self.ele).select_by_visible_text(text)

    def select_index(self, index):
        Select(self.ele).select_by_index(index)

    def __call__(self):
        return self.ele
