import urllib.request
import urllib.error
import urllib.parse

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


browser = webdriver.Chrome()


url = "https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com"
browser.get(url)
print(browser.title)

SeleniumWait("id", 5)

myId = browser.find_element_by_id('id')
myId.send_keys('thks10')

