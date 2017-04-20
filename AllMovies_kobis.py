import urllib2  
import string
import os
import re
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import logging  
import ssl
import Config
logging.basicConfig(filename=Config.LOG_PATH,level=logging.DEBUG)

ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PARSE_API_ROOT"] = Config.PARSE_SERVER_URI

from parse_rest.datatypes import Function, Object, GeoPoint, File
from parse_rest.connection import register
from parse_rest.query import QueryResourceDoesNotExist
from parse_rest.connection import ParseBatcher
from parse_rest.core import ResourceRequestBadRequest, ParseError

register(Config.APPLICATION_ID, "", master_key=Config.MASTER_KEY)
reload(sys)
sys.setdefaultencoding('utf-8')

# for saving server progress to backend
class Parsing(Object):
    pass

class Parsing_err(Object):
    pass

# currError = Parsing_err(page_num=0, entity_num=1, err_url="test", status="pending")
# currError.save()
# print "saved"

url = ("http://kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do")
print url

#idx= 0
#page = urllib2.urlopen(url)        
#soup = BeautifulSoup(page, "lxml")

browser = webdriver.Chrome()
browser.get(url)

try:
    elem = browser.find_element_by_name('sOpenYearS')
    elem.send_keys('2004-01-01')

    elem = browser.find_element_by_name('sOpenYearE')
    elem.send_keys('2016-12-31')

    browser.execute_script("fn_searchList();")

    soup = BeautifulSoup(browser.page_source, "lxml")
    a= soup.find("div", { "class":"board_btm" })
    print a.em.text

    table= soup.find("table", {"class":"boardList03"})
    arrMovies= table.tbody.find_all("tr")

    for idx,movie in enumerate(arrMovies):
        click_content= movie.td.a['onclick']
        movieNum= re.sub(r'\D', "", click_content) # sub non-digits by regex

        if movieNum:
            print movieNum
            browser.execute_script("dtlExcelDn('movie','box','" + movieNum + "')" )
            alert = browser.switch_to_alert()
            alert.accept()
        else:
            print "nothing found!"
except:
    print "no alert to accept"
finally:
    browser.quit()