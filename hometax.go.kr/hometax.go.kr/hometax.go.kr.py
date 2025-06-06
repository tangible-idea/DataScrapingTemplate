
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
browser = webdriver.Chrome()

def SeleniumWait(id, delay):
    while True:
            try:
                myElem = WebDriverWait(browser, delay).until(
                    EC.presence_of_element_located((By.ID, id)))
                print("Page is ready!")
                # it will break from the loop once the specific element will be present.
                break
            except TimeoutException:
                print("Loading took too much time!")
                browser.quit()
                return

def SeleniumWaitClass(className, delay):
    while True:
            try:
                myElem = WebDriverWait(browser, delay).until(
                    EC.presence_of_element_located((By.CLASS_NAME, className)))
                print("Page is ready!")
                # it will break from the loop once the specific element will be present.
                break
            except TimeoutException:
                print("Loading took too much time!")
                browser.quit()
                return

def TryToParse(TESTorREAL):

    # PARSING_COUNT = PARSING_COUNT + 1  # add count

    # target url
    print("TryToParse()")
    print("")

    try:
        url = "https://www.hometax.go.kr/"

        
        # browser.implicitly_wait(11) # seconds
        browser.get(url)
        print(browser.title)
        
        SeleniumWait("group88615548", 30)
        print("loginbtn found")
        #select = Select(browser.find_element_by_id('identifierId'))
        loginbtn = browser.find_element_by_id('group88615548')
        loginbtn.click()
        browser.implicitly_wait(5)

        #browser.execute_script("$('#anchor15').click();")
        #browser.execute_script("alert('test');")
        #SeleniumWait("anchor15", 20) #iptUserPw
        #loginmethodbtn = browser.find_element_by_id('anchor15')
        #loginmethodbtn.click()
        #browser.implicitly_wait(1)

        SeleniumWait("iptUserId", 30) #iptUserPw
        print("iptUserId found")
        email = browser.find_element_by_id('iptUserId')
        email.send_keys('tangibleidea')
        email.send_keys(Keys.ENTER)
        browser.implicitly_wait(5)

        #pw = browser.find_element_by_css_selector("input[aria-label='비밀번호 입력']")
        #pw.send_keys('')
        #pw.send_keys(Keys.ENTER)
        #browser.implicitly_wait(5)

        SeleniumWaitClass("docs-title-save-label-text", 100)
        history_btn = browser.find_element_by_css_selector(".docs-title-save-label-text")#.click()
        #history_btn = browser.find_element_by_class('docs-title-save-label-text')
        history_btn.click()


        #SeleniumWaitClass("docs-revisions-tile-header", 100)
        #browser.implicitly_wait(5)
        #time.sleep(15)
        print("Please click the arrows.")
        # code to load webpage, automatically fill whatever can be entered
        x = input("Enter p when done.")
        # Enter the data on page manually. Then come back to terminal and type YES and then press enter.
        if x == 'p':
            #browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #browser.implicitly_wait(5)

            # clicking arrow part is not completed
            # arrow_list= browser.find_elements_by_css_selector(".docs-revisions-tile-arrow-button")
            # for arrow in arrow_list:
            #     arrow.click()
            # browser.implicitly_wait(5)                

            history_list = browser.find_elements_by_css_selector(".docs-revisions-tile-header")#.click()
            #history_btn = browser.find_element_by_class('docs-title-save-label-text')

            history_thismonth = []
            for item in history_list:
                text= item.text
                print(text)
                if "October" in text:
                   history_thismonth.append(text)
                   print(item.text)
            #     datetime_object = datetime.strptime(text, "%B %d, %I:%M %p")
            #     print(datetime_object)

            #docs-revisions-tile-arrow-button
            #docs-revisions-tile-arrow-button

            print(len(history_thismonth))
            for item in history_thismonth:
                #print(item)
                item = item + ", 2019"
                datetime_object = datetime.strptime(item, "%B %d, %I:%M %p, %Y")
                print(datetime_object)

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
