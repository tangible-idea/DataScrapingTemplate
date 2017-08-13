# written in python 3.x
import urllib.request
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

def add_empty_data(arrData, count):
    for i in range(0,count):
        arrData.append(" ")
    return arrData

def get_detail_of_blog(href):
    arrData = []

    if(href.find("blog.me") != -1): # if it's blog.me
        href= href.replace("http://", "")
        splited_href= href.split('.')
        if(len(splited_href) == 3):
            #print(splited_href)
            arrData.append(splited_href[0])
    elif(href.find("blog.naver.com") != -1): # if it's blog.me
        href= href.replace("http://", "")
        splited_href= href.split('/')
        if(len(splited_href) == 2):
            #print(splited_href)
            arrData.append(splited_href[1])

    return arrData
    

def get_all_networks():  
    #count var
    
    GOT_ERROR = False
    LAST_ERR_PAGE= 0
    LAST_ERR_IDX= 0

    ID = "happycymbals"
    PAGE_MIN= 1
    PAGE_MAX= 1
    DATA_PER_PAGE = 20

    WebsiteName="blog.naver.com"
    filePath= "Output_"+WebsiteName+".txt"

    # spliter between tasks
    text_file = open(filePath, "a")
    text_file.write("\n")
    text_file.close()

    #task.status = "working"
    #print("Now assigned to the server and begin the task.")
    #task.save()

    url_first = ("http://section.blog.naver.com/connect/ViewMoreFollowers.nhn?blogId="+str(ID)+"&currentPage=0&widgetSeq=554118")
    request_1= urllib.request.Request(url_first)
    page_1 = urllib.request.urlopen(request_1)       
    soup_1 = BeautifulSoup(page_1, "lxml")
    total_network = soup_1.find("div", { "class":"function_box buddy_cnt_admin" })
    if(total_network is not None):
        count_of_networks= int(total_network.p.strong.text)
        PAGE_MAX= count_of_networks / DATA_PER_PAGE + 1
        print("PAGE_MAX is set to : " +str(int(PAGE_MAX)))

    for num in range(PAGE_MIN, int(PAGE_MAX)):
        url = ("http://section.blog.naver.com/connect/ViewMoreFollowers.nhn?blogId="+str(ID)+"&currentPage="+str(num)+"&widgetSeq=554118")
        #print(url)
        #try:
        #idx= 0
        request= urllib.request.Request(url)
        page = urllib.request.urlopen(request)       
        soup = BeautifulSoup(page, "lxml")

        #if num == PAGE_MIN:
        #    init_page(soup, task)

        #task.last_page= url
        #task.save()

        item_wrapped_ul = soup.find("ul", { "class":"my_buddy_list" })
        items_a = item_wrapped_ul.findAll("a", { "class":"imgbox" })
        print("item count in this page : "+ str(len(items_a)))

        countitem_perpage= len(items_a)
        for idx,item in enumerate(items_a):
        #     if single_test_mode is True:
        #         if idx != 49:
        #             continue
            #print(item)
            item_href= item['href']
            #item_name= item.span.findNext('span').text

            # count_percentage = count_total / ((PAGE_MAX-PAGE_MIN)*ITEMS_PER_PAGE)
            # count_total += 1
            # print('{:.2%}'.format(count_percentage))

            #task.done_count = count_total
            #task.save()

            print(item_href)
            arrData= get_detail_of_blog(item_href)
            #movies_list.append([item_href, item_name])

            
            #strCombineData=""
            text_file = open(filePath, "a")
            for data in arrData:
                text_file.write(str(data) + "@naver.com")
            text_file.write('\n')
            text_file.close()
                #strCombineData += (data + "|")
            #print strCombineData
            #
        # except Exception, e:
        #     logging.exception(e)
        #     LAST_ERR_IDX = idx
        #     LAST_ERR_PAGE = num
        #     GOT_ERROR = True
        #     currError = Parsing_err(page_num=num, entity_num=idx, err_url=url, status="pending")
        #     currError.save()
        #     relation= currError.relation("Parsing_range")


    return filePath

get_all_networks()