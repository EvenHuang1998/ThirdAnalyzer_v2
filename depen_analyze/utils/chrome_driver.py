#coding: utf-8
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver

def get_driver(set_proxy = False, path_to_driver = "./resources/chromedriver"):
    '''初始化headless的chromedriver并返回'''
    PROXY = "127.0.0.1:7890"
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    if set_proxy:
        options.add_argument(f"--proxxy-server={PROXY}")
    # options.add_argument("--proxy-server={0}".format(url))

    return webdriver.Chrome(path_to_driver, options=options, desired_capabilities=caps)