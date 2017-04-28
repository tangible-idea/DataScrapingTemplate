#-*- coding: utf-8 -*-
import urllib2  
import string
import os
from shutil import move
import re
import sys
import time
import glob
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
USER_NAME= "fanta"

def move_to_download_folder(downloadPath, newFileName, fileExtension):
    got_file = False   
    ## Grab current file name.
    while got_file == False:
        try: 
            currentFile = glob.glob(downloadPath + "*.xls")
            if len(currentFile) != 0:
                got_file = True

        except:
            print "File has not finished downloading"
            time.sleep(1)
    
    # Validate windows path by regex
    cleaned_up_filename = re.sub(r'[/\\:*?"<>|]', '', newFileName)

    ## Create new file name
    #fileDestination = "C:\\Users\\" + USER_NAME +"\\Source\\Repos\\Movie_DataMiner\\KOBIS_download\\" + cleaned_up_filename +"." + fileExtension
    fileDestination = ".\\KOBIS_download\\" + cleaned_up_filename +"." + fileExtension
    print "fileDestination : " +fileDestination
    #os.rename(currentFile[0], fileDestination)
    move(currentFile[0], fileDestination)
    return

def FindAndAcceptAlert(browser):
    try:
        alert = None
        while(True): # check till alert is popped up
            alert = isAlertPresent(browser)
            if alert is not None:
                alert.accept()
                return
    except:
        return

def isAlertPresent(browser):
   try:
        alert= browser.driver.switch_to_alert()
        return alert
   except NoAlertPresentException: 
        return None

def extractMovieNum(txt):
    movieNum= re.sub(r'\D', "", txt) # sub non-digits by regex
    if len(movieNum) == 8:
        return movieNum
    else:
        del1= txt.find(",")
        del2= txt.find(")")
        movieNum= txt[del1+1:del2].replace("'","")
        if len(movieNum) == 8:
            return movieNum
        else:
            return None

def parseThisPage(browser, page_num):
    browser.execute_script("goPage('" + str(page_num) + "')" )

    time.sleep(1)

    soup = BeautifulSoup(browser.page_source, "lxml")
    table= soup.find("table", {"class":"boardList03"})
    arrMovies= table.tbody.find_all("tr")

    for idx,movie in enumerate(arrMovies):
        click_content= movie.td.a['onclick']
        movieName= movie.td.a.text
        movieNum= extractMovieNum(click_content)

        if movieNum:
            print movieNum +","+ movieName
            # dtlExcelDn('movie','box','20080828');
            browser.execute_script("dtlExcelDn('movie','box','" + movieNum + "');" )
            #print result
            
            #wait = WebDriverWait(browser, 10)
            #wait.until(EC.alert_is_present)
            time.sleep(1)
            alert= browser.switch_to_alert()
            alert.accept()

            move_to_download_folder("C:\\Users\\"+USER_NAME+"\\Downloads\\", movieName + "_"+ str(movieNum), "xls")
            #FindAndAcceptAlert(browser)
        else:
            print "couldn't find movie corresponding with : "+ movieName

url = ("http://kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do")
print url

MOVIES_PER_PAGE= 10

#Chrome driver setting
#options = webdriver.ChromeOptions() 
#options.add_argument("download.default_directory=./KOBIS_download")
#browser = webdriver.Chrome(chrome_options=options)
browser = webdriver.Chrome()

# Firefox : To prevent download dialog
# profile = webdriver.FirefoxProfile()
# profile.set_preference('browser.download.folderList', 2) # custom location
# profile.set_preference('browser.download.manager.showWhenStarting', False)
# profile.set_preference('browser.download.dir', '/KOBIS_download')
# profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/vnd.ms-excel')
#browser = webdriver.Firefox()

browser.implicitly_wait(3) # seconds
browser.get(url)

try:
    elem = browser.find_element_by_name('sOpenYearS')
    elem.send_keys('2004-01-01')

    elem = browser.find_element_by_name('sOpenYearE')
    elem.send_keys('2016-12-31')

    browser.execute_script("fn_searchList();")
    time.sleep(0.5)

    soup = BeautifulSoup(browser.page_source, "lxml")
    countMovies= soup.find("div", { "class":"board_btm" })
    countMovies_filtered= re.sub(r'\D', "", countMovies.em.text)
    print "retrieved movies : "+countMovies_filtered
    TOTAL_PAGES = (int(countMovies_filtered) / MOVIES_PER_PAGE)+1
    print "total pages : "+ str(TOTAL_PAGES)

    STARTING_PAGE= 457
    for x in range(STARTING_PAGE, TOTAL_PAGES):
        print "current page : " + str(x)
        parseThisPage(browser, x)
except Exception, e:
    print str(e)
finally:
    browser.quit()