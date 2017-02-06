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
from AllMovies_imdb import upload_data, add_empty_data, get_connections, get_business_of_movie, get_companycredits_of_movie, get_fullcredits_of_movie, get_releaseinfo_of_movie, get_techinfo_of_movie, get_detail_of_movie, register_toServer, init_page

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

class Parsing_err2(Object):
    pass

def check_errsheets(currServer):
    errsheets = Parsing_err.Query.all().limit(1000)
    todo = None
    for sheet in errsheets:
        if (sheet.status == "pend") or (sheet.status == "pending") or (sheet.status == ""):
            todo= sheet
            break
    if todo is None:
        print "There's nothing to do anymore."
        return None
    else:
        print 'Found the err tasks.'
        return todo


def get_err_movies(session, task):  
    #count var
    ERR_PAGE= task.page_num
    ERR_IDX= task.entity_num
    ITEMS_PER_PAGE= 50.0
    count_total= 0
    filePath= "Output_Err_page_"+str(ERR_PAGE)+"_idx_"+str(ERR_IDX)+".txt"

    # spliter between tasks
    text_file = open(filePath, "a")
    text_file.write("\n")
    text_file.close()

    task.status = "working"
    print "Now assigned to the server and begin the task."
    task.save()

    url= task.err_url
    print url
    try:
        idx= 0
        page = urllib2.urlopen(url)        
        soup = BeautifulSoup(page, "lxml")

        task.last_page= url
        task.save()

        items = soup.findAll("span", { "class":"lister-item-header" })
        print "item count in this page : "+ str(len(items))

        for idx,item in enumerate(items):
            print "page : "+str(ERR_PAGE)+", idx : "+str(idx) + " out of " + str(ITEMS_PER_PAGE) + ", ERR_IDX was " + str(ERR_IDX)
            if idx < ERR_IDX:
                print "skip"
                continue
            
            item_href= item.span.findNext('span').a['href']
            item_name= item.span.findNext('span').text

            
            count_total += 1
            task.done_count = count_total
            task.save()

            arrData= get_detail_of_movie(item_href, item_name)

            text_file = open(filePath, "a")
            for data in arrData:
                text_file.write(str(data) + "|")
            text_file.write('\n')
            text_file.close()

    except Exception, e:
        logging.exception(e)
        print e
        currError = Parsing_err2(page_num=task.page_num, entity_num=idx, err_url=url)
        currError.save()
        relation= currError.relation("Parsing_err")
        relation.add(task)


    return filePath

#Here's the main
while True:
    session= register_toServer() # 1. try to register
    todo = check_errsheets(session) # 2. obtain the todo list

    if todo is None:    # 3. if no longer things to do, exit
        print "Done."
        break
    else:
        fileuri= get_err_movies(session, todo)   # 4. if it has things to do, do work.
        if fileuri == "":
            print "There's no file."
            todo.status = "done"
            todo.save()
        else:
            upload_data(session, todo, fileuri)
