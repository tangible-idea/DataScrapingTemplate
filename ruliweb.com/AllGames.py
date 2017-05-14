# written by python 2.*
import urllib2  
import string
import os
import re
import sys
from datetime import datetime
from bs4 import BeautifulSoup  
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

register(Config.APPLICATION_ID, Config.REST_API_KEY, master_key=Config.MASTER_KEY)
reload(sys)
sys.setdefaultencoding('utf-8')

# for saving server progress to backend
class Parsing(Object):
    pass

class Parsing_err(Object):
    pass

class Parsing_range(Object):
    pass

def add_empty_data(arrData, count):
    for i in range(0,count):
        arrData.append(" ")
    return arrData


def get_all_movies(session, task, single_test_mode):  
    #count var
    
    GOT_ERROR = False
    LAST_ERR_PAGE= 0
    LAST_ERR_IDX= 0

    WebsiteName="ruliweb"
    filePath= "Output_"+WebsiteName+".txt"

    # spliter between tasks
    text_file = open(filePath, "a")
    text_file.write("\n")
    text_file.close()

    print "Current page : " + START_YEAR + " to " + END_YEAR
    print "Quantity : " + str(task.quantity)
    task.status = "working"
    print "Now assigned to the server and begin the task."
    task.save()

    for num in range(PAGE_MIN, PAGE_MAX):
        url = ("http://www.imdb.com/search/title?sort="+SORTS
                +",asc&start=1&title_type=feature&year="
                +str(START_YEAR)+","+str(END_YEAR)+"&view=simple"
               "&page=" + str(num))
        print url
        try:
            idx= 0
            page = urllib2.urlopen(url)        
            soup = BeautifulSoup(page, "lxml")

            if num == PAGE_MIN:
                init_page(soup, task)

            task.last_page= url
            task.save()

            items = soup.findAll("span", { "class":"lister-item-header" })
            print "item count in this page : "+ str(len(items))

            #countitem_perpage= len(items)
            for idx,item in enumerate(items):
                if single_test_mode is True:
                    if idx != 49:
                        continue
                
                item_href= item.span.findNext('span').a['href']
                item_name= item.span.findNext('span').text

                count_percentage = count_total / ((PAGE_MAX-PAGE_MIN)*ITEMS_PER_PAGE)
                count_total += 1
                print '{:.2%}'.format(count_percentage)
                #print "{0:.0f}%".format(count_percentage *100)
                #task.progress = count_percentage
                task.done_count = count_total
                task.save()

                arrData= get_detail_of_movie(item_href, item_name)
                #movies_list.append([item_href, item_name])

                
                #strCombineData=""
                text_file = open(filePath, "a")
                for data in arrData:
                    text_file.write(str(data) + "|")
                text_file.write('\n')
                text_file.close()
                    #strCombineData += (data + "|")
                #print strCombineData
                #
        except Exception, e:
            logging.exception(e)
            LAST_ERR_IDX = idx
            LAST_ERR_PAGE = num
            GOT_ERROR = True
            currError = Parsing_err(page_num=num, entity_num=idx, err_url=url, status="pending")
            currError.save()
            relation= currError.relation("Parsing_range")


    return filePath

