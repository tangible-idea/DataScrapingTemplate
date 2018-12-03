
# written by python 2.*
from urllib.request import urlopen
import string
import os
import re
import sys
from datetime import datetime
from bs4 import BeautifulSoup  


def add_empty_data(arrData, count):
    for i in range(0,count):
        arrData.append(" ")
    return arrData


def get_all_movies():  
    #count var
    filePath= "Output_naver.movie.csv"

    arrData = []
    # spliter between tasks
    text_file = open(filePath, "a")
    text_file.write("\n")
    text_file.close()

    PAGE_MIN= 1
    PAGE_MAX= 681
    ITEMS_PER_PAGE= 10
    count_total= 0
    for num in range(PAGE_MIN, PAGE_MAX):
        url = ("https://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code=154255&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false"
                +"&page=" + str(num))
        print(url)
        idx= 0
        page = urlopen(url)        
        soup = BeautifulSoup(page, "html.parser")

        items_temp = soup.find("div", { "class":"score_result" })
        #print(items_temp)
        items = items_temp.ul.findAll("li")
        print("item count in this page : "+ str(len(items)))

        arrData.clear()
        #countitem_perpage= len(items)
        for idx,item in enumerate(items):
            item_score= item.find("div", { "class":"star_score" }).text.replace('\n','')
            score_reple_text= item.find("div", { "class":"score_reple" }).text
            splited_review= score_reple_text.split('\n\n\n\n\n')
            if len(splited_review) >= 2:
                item_review= splited_review[0].replace('\n','')
            else:
                item_review =' '

            count_percentage = count_total / ((PAGE_MAX-PAGE_MIN)*ITEMS_PER_PAGE)
            count_total += 1
            #print '{:.2%}'.format(count_percentage)
            
            arrData.append(item_score+ "    " +item_review)

        text_file = open(filePath, "a")
        for data in arrData:
            text_file.write(str(data))
            text_file.write('\n')
        text_file.close()
        #

    return filePath

get_all_movies()