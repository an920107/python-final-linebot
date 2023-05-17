import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import os
import time
import json

from modules.chrome import Chrome


def main():

    URL = "https://irs.thsrc.com.tw/IMINT/"

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    chrome = Chrome(options=options)
    chrome.set_window_size(1600, 1000)

    chrome.get(URL)

    # 同意 cookie
    try:
        chrome.find_element_and_wait(
            By.XPATH, "//*[@id='cookieAccpetBtn']", 100000).click()
    except:
        return

    # 輸入訂票資訊
    Select(chrome.find_element(
        By.XPATH, "//*[@id='select_location01']")).options
    # Select(chrome.find_element(
    #     By.XPATH, "//*[@id='select_location01']")).select_by_value("3")
    # Select(chrome.find_element(
    #     By.XPATH, "//*[@id='select_location02']")).select_by_value("5")
    # chrome.find_element(By.XPATH, "//*[@id='Departdate02']").send_keys("2023/05/30")


if __name__ == "__main__":
    main()
    time.sleep(1000)
