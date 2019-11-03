# written in python 3.7
import urllib.request
import urllib.error
import urllib.parse
from threading import Timer
from time import sleep
import time
import string
import os
import re
import sys
import logging
from datetime import datetime

# pip install BeautifulSoup4
# pip install lxml
from bs4 import BeautifulSoup

# pip install selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
import ssl

logging.basicConfig(filename="log.txt",
                    format='%(asctime)s %(message)s', level=logging.DEBUG)
# create logger
logger = logging.getLogger('simple_example')


def TryToParse(TESTorREAL):

    # PARSING_COUNT = PARSING_COUNT + 1  # add count

    # target url
    print("TryToParse()")

    try:
        #url = "https://s3.ap-northeast-2.amazonaws.com/mitchin/web/sign.html"
        url = "https://docs.google.com/spreadsheets/d/1iUkEp4rFI-rJIQThCM0E3MVXx_a6RWJ1kSqMpkCHrXM/edit#gid=116309450"
        # if TESTorREAL == "TEST":
        #     url = "http://softinus.com/upbit_tracker/upbit_tdd1.html"

        browser = webdriver.Chrome()
        # browser.implicitly_wait(11) # seconds
        browser.get(url)
        print(browser.title)
        delay = 100  # seconds
        while True:
            try:
                myElem = WebDriverWait(browser, delay).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "btn-success")))
                print("Page is ready!")
                # it will break from the loop once the specific element will be present.
                break
            except TimeoutException:
                print("Loading took too much time!")
                browser.quit()
                return

        print("test")
        select = Select(browser.find_element_by_id('Category'))

        # select by visible text
        print("select_by_visible_text: All")
        result1 = select.select_by_value('All')

        print("select_by_visible_text: All: " + result1)
        browser.implicitly_wait(11)  # seconds
        # select by value
        # select.select_by_value('1')

        # #wait = WebDriverWait(driver, 10)
        # #element = wait.until(EC.element_to_be_clickable((By.ID, 'someid')))

        # soup = BeautifulSoup(browser.page_source, "lxml")
        # #page = urllib2.urlopen(url)
        # #soup = BeautifulSoup(page, "lxml")

        # ul_top = soup.find("ul", {"class": "ty05"})
        # div_scrollB = ul_top.findNext('div').find("div", {"class": "scrollB"})
        # strPriceList = div_scrollB.div.div.table.tbody.text.strip()
        # arrPriceList = strPriceList.split('--')
        # # print arrPriceList
        # #str_count_caption= "총 " +str(len(arrPriceList)) +" 개 코인\n"
        # # save last total coin count here except 1st row
        # LAST_TOTAL_COIN_COUNT = len(arrPriceList) - 1
        # print(str(LAST_TOTAL_COIN_COUNT))

        # LAST_UNDER_READY_COIN_COUNT = 0
        # for coin in arrPriceList:
        #     if "준비중" in coin:
        #         LAST_UNDER_READY_COIN_COUNT = LAST_UNDER_READY_COIN_COUNT + 1

        # browser.quit()
    except Exception as e:
        logging.exception(e)
        print(e)
        #sendTelegramMsg("TryToParse()에서 Exception 발생 : " + str(e))
        pass
    # except StaleElementReferenceException:  # ignore this error
    #     pass  # TODO: consider logging the exception
    finally:
        pass


TryToParse(True)
