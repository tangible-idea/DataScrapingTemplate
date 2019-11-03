from urllib.request import urlopen
import ssl
from bs4 import BeautifulSoup
import time

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

def SeleniumWait(className, delay):
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

url = "https://audioclip.naver.com/panels/rank/channels"
browser = webdriver.Chrome()
browser.get(url)

SeleniumWait("detail_title", 5)

context = ssl._create_unverified_context()
#page = urlopen(url, context=context)


browser.execute_script("window.scrollTo(0, 1080)") 
# Wait to load page
time.sleep(3)
#print(soup)

soup = BeautifulSoup(browser.page_source, "lxml")

tables = soup.find_all("div", {"class", "detail_title"})
for idx, t in enumerate(tables):
	print(str(idx+1) + ". " + t.text)