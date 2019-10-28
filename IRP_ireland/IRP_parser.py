# written in python 3.7
#-*- coding: utf-8 -*-
import urllib2  
# import urllib.request
# import urllib.error
# import urllib.parse
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

reload(sys)
sys.setdefaultencoding('utf-8')


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
        url = "https://burghquayregistrationoffice.inis.gov.ie/Website/AMSREG/AMSRegWeb.nsf/AppSelect?OpenForm"
        # if TESTorREAL == "TEST":
        #     url = "http://softinus.com/upbit_tracker/upbit_tdd1.html"

        browser = webdriver.Firefox('/0.Devs/DataScrapingTemplate/IRP_ireland/geckodriver')
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

        print("select_by_visible_text: All: " + str(result1))
        browser.implicitly_wait(11)  # seconds
        # browser.quit()
    except Exception as e:
        logging.exception(e)
        print(e)
        pass
    # except StaleElementReferenceException:  # ignore this error
    #     pass  # TODO: consider logging the exception
    finally:
        pass


TryToParse(True)
