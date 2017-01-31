import urllib2  
import string
import os
import re
import sys
from datetime import datetime
from bs4 import BeautifulSoup  
import logging  
logging.basicConfig(filename=Config.LOG_PATH,level=logging.DEBUG)
import ssl
import Config

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

def get_connections(item_herf, arrData):
    url = item_herf + "trivia?tab=mc"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, "lxml")

    #print url
    #34. connections
    strConnection = ""
    connections= soup.findAll("div", {"class", "soda"})
    if len(connections) == 0:
        add_empty_data(arrData, 0)
        #print "no any connections"
    else:
        #print connections[0].text.strip()
        if connections[0].text.strip().startswith("It looks like we don't have any Connections for this title yet.") == True:
            add_empty_data(arrData, 0)
        else:
            for conn in connections:
                strConnection += str.join("", conn.text.splitlines()).strip() + " ; "
            arrData.append(strConnection)
   
    #print strConnection
    return arrData


def get_business_of_movie(item_herf, arrData):
    url = item_herf + "business"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, "lxml")

    strBudget= strOW= strGross= strWGross= strAdmis= strRentals= strFlimingDates= strCopyright=""
    #businessData= []

    content= soup.find(id="tn15content")
    if content is not None:
        for idx,h5 in enumerate(content.prettify().split('<h5>')): # one block
            if idx == 0: # exclude zero idx
                continue
            
            h5= str.join(" ", h5.splitlines()).rstrip()
            #print h5
            soup2 = BeautifulSoup(''.join(h5), "lxml")
            strBuf= soup2.text
            strBuf= str.join("", strBuf.splitlines()).strip()
            firstWord= h5.split("</h5>")[0].strip()
            #print firstWord
            strBuf= strBuf.replace(firstWord, "", 1)
            
            if firstWord == "Budget":
                strBudget = strBuf
            elif firstWord == "Opening Weekend":
                strOW = strBuf
            elif firstWord == "Gross":
                strGross = strBuf
            elif firstWord == "Weekend Gross":
                strWGross = strBuf
            elif firstWord == "Admissions":
                strAdmis = strBuf
            elif firstWord == "Rentals":
                strRentals = strBuf
            elif firstWord == "Filming Dates":
                strFlimingDates = strBuf
            elif firstWord == "Copyright Holder":
                strCopyright = strBuf

    if(strBudget == ""):
        arrData.append(" ")
    else:
        arrData.append(strBudget)

    if(strOW == ""):
        arrData.append(" ")
    else:
        arrData.append(strOW)

    if(strGross == ""):
        arrData.append(" ")
    else:
        arrData.append(strGross)

    if(strWGross == ""):
        arrData.append(" ")
    else:
        arrData.append(strWGross)

    if(strAdmis == ""):
        arrData.append(" ")
    else:
        arrData.append(strAdmis)

    if(strRentals == ""):
        arrData.append(" ")
    else:
        arrData.append(strRentals)     

    if(strFlimingDates == ""):
        arrData.append(" ")
    else:
        arrData.append(strFlimingDates) 

    if(strCopyright == ""):
        arrData.append(" ")
    else:
        arrData.append(strCopyright) 
        
    return arrData

def get_companycredits_of_movie(item_herf, arrData):
    url = item_herf + "companycredits"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, "lxml")

    strProductionCo= ""
    strDistributors= ""
    allList= soup.findAll("ul", {"class", "simpleList"})

    if len(allList) != 0:
        for oneList in allList:
            h4 = oneList.find_previous_sibling('h4')
            if h4.text == "Production Companies":
                one = oneList.findAll("li")
                for content in one:
                    strProductionCo += (content.text + ", ")
            elif h4.text == "Distributors":
                one = oneList.findAll("li")
                for content in one:
                    strDistributors += (content.text + ", ")

    strProductionCo= str.join("", strProductionCo.splitlines()).strip()
    strDistributors= str.join("", strDistributors.splitlines()).strip()
    # todo: exception hanling
    arrData.append(strProductionCo)
    arrData.append(strDistributors)
    return arrData


def get_fullcredits_of_movie(item_herf):
    url = item_herf + "fullcredits"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, "lxml")

    listCastList= []
    table_casts= soup.find("table", {"id", "cast_list"})
    if table_casts is not None:
        each_cast = table_casts.findAll("tr")
        #print len(each_cast)
        if len(each_cast) <= 15:
            for cast in each_cast:
                listCastList.append(cast.td.findNext('td').text)
        else:
            for x in range(1, 16):
                listCastList.append(each_cast[x].td.findNext('td').text)

    #combine
    strCasts= ""
    for cast in listCastList:
        strCasts += cast.strip() + ", "

    strCasts = str.join("", strCasts.splitlines())
    #print strCasts.strip()
    return strCasts


def get_releaseinfo_of_movie(item_tech_href):
    url = item_tech_href + "releaseinfo"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, "lxml")

    listReleaseDateList= []
    table_release_date= soup.find("table", { "id":"release_dates" })
    if table_release_date is not None:
        each_release_date= table_release_date.findAll("tr")
        #print len(each_release_date)
        if len(each_release_date) is not 0:
            for releasedate in each_release_date:
                RD_col1= str.join("", releasedate.td.text.splitlines()).strip()
                RD_col2= str.join("", releasedate.td.findNext('td').text.splitlines()).strip()
                RD_col3= str.join("", releasedate.td.findNext('td').findNext('td').text.splitlines()).strip()
                listReleaseDateList.append([RD_col1, RD_col2, RD_col3])
    
    #combine
    strReleaseDate= ""
    for rd in listReleaseDateList:
        strReleaseDate += (rd[0]+ " : "+rd[1] +" " +rd[2] + ", ")

    return strReleaseDate

def get_techinfo_of_movie(item_tech_href, arrData):
    url = item_tech_href + "technical"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, "lxml")

    runtime= soup.body.tbody.find(text=" Runtime ")
    if runtime is not None:
        strRuntime= runtime.findNext().text.strip().replace('|','')
        strRuntime= str.join("", strRuntime.splitlines()).strip()
        arrData.append(strRuntime)
    else:
        arrData.append(" ")

    color= soup.body.tbody.find(text=" Color ")
    if color is not None:
        strColor= color.findNext().text.strip().replace('|','')
        strColor= str.join("", strColor.splitlines()).strip()
        arrData.append(strColor)
    else:
        arrData.append(" ")

    filmLen= soup.body.tbody.find(text=" Film Length ")
    if filmLen is not None:
        strFlimLen= filmLen.findNext().text.strip().replace('|','')
        strFlimLen= str.join("", strFlimLen.splitlines()).strip()
        arrData.append(strFlimLen)
    else:
        arrData.append(" ")

    return arrData


def get_detail_of_movie(item_href, item_name):

    arrData = []

    item_href = item_href.replace("?ref_=adv_li_tt", "")
    url2 = "http://www.imdb.com" + item_href
    page2 = urllib2.urlopen(url2)
    soup2 = BeautifulSoup(page2, "lxml")

    # 1. Movie Name, 2. Link
    item_name = str.join("", item_name.splitlines()).rstrip()
    arrData.append(item_name)
    arrData.append(url2)

    # 3. Director, 4. Writers, 5. Stars
    nDirectorExist = -1
    nWriterExist = -1
    nStarsExist = -1

    credit_summary_items = soup2.findAll("div", { "class":"credit_summary_item" })
    for idx,summary_item in enumerate(credit_summary_items):
        if summary_item.h4.text == "Director:" or summary_item.h4.text == "Directors:":
            nDirectorExist= idx
        elif summary_item.h4.text == "Writer:" or summary_item.h4.text == "Writers:":
            nWriterExist= idx
        elif summary_item.h4.text == "Star:" or summary_item.h4.text == "Stars:":
            nStarsExist= idx

    #print "Director : "+str(nDirectorExist) + ", Writer : " + str(nWriterExist) + ", Stars : " + str(nStarsExist)

    if nDirectorExist != -1:
        strDirector= ""
        arrDirectors= credit_summary_items[nDirectorExist].findAll("span", {"itemprop":"director"})
        for director in arrDirectors:
            strDirector += director.a.span.text.strip()
            strDirector += ", "
        arrData.append(strDirector)
        #print strDirector
    else:
        arrData= add_empty_data(arrData, 1)

    if nWriterExist != -1:
        strWriters= ""
        arrWriters= credit_summary_items[nWriterExist].findAll("span", {"itemprop":"creator"})
        for writer in arrWriters:
            strWriters += writer.a.span.text.strip()
            strWriters += ", "
        arrData.append(strWriters)
        #print strWriters
    else:
        arrData= add_empty_data(arrData, 1)

    if nStarsExist != -1:
        arrData.append( get_fullcredits_of_movie(url2) )
    else:
        arrData= add_empty_data(arrData, 1)

    # 6. Nomination
    nominations = soup2.findAll("span", { "itemprop":"awards" })
    if len(nominations) != 0:
        nomin_1L = ""
        for nomins in nominations:
            nomin_1L += nomins.text.strip()
             #print nomins.text.rstrip()
        nomin_1L = str.join("", nomin_1L.splitlines())
        arrData.append( nomin_1L.strip() )
    else:
        arrData.append(" ")

    # 7. Reviews, 8. Critics, 9. Popularity 
    reviewbar_items = soup2.findAll("div", { "class":"titleReviewBarItem" })

    nMetaScore = -1
    nReview = -1
    nCritics= -1
    nPopularity = -1

    #print "Reviewbar items count : "+str(len(reviewbar_items))
    for idx,item in enumerate(reviewbar_items):
        metaScore= item.find("div", { "class":"metacriticScore" })
        #print item.div.text
        if metaScore is not None:
            strMetaScore = metaScore.span.text
            nMetaScore = idx
        if str.join("", item.div.text.splitlines()).strip() == "Reviews":
            reviews= item.find("span", { "class":"subText" })
            if reviews is not None:
                strText1= reviews.findNext('a').text.replace('|','')
                strText1= str.join("", strText1.splitlines()).strip()
                strText2= reviews.findNext('a').findNext('a').text.replace('|','')
                strText2= str.join("", strText2.splitlines()).strip()
                #print "strText1 : " + strText1
                #print "strText2 : " + strText2
                if strText1.find("critic") != -1: # N critic | ???
                    nCritics = idx
                    strCritics = strText1
                    if strText2.find('user') != -1: # N critic | N user
                        nReview = idx
                        strReviewUsers = strText2

                elif strText1.find('user') != -1: # N user | ???
                    nReview = idx
                    strReviewUsers = strText1
                    if strText2.find("critic") != -1: # N user | N critic
                        nCritics = idx
                        strCritics = strText2

        subItemOfPopu= item.div.findNext('div').div
        #print subItemOfPopu
        if subItemOfPopu is not None:
            if str.join("", subItemOfPopu.text.splitlines()).strip() == "Popularity":
                popu= item.find("span", { "class":"subText" })
                if popu is not None:
                    nPopularity= idx
                    strPopularity = str.join("", popu.text.splitlines()).strip()
                    #print strPopularity

    if nReview != -1:
        arrData.append(strReviewUsers)
    else:
        arrData= add_empty_data(arrData, 1)

    if nCritics != -1:
        arrData.append(strCritics)
    else:
        arrData= add_empty_data(arrData, 1)   

    if nPopularity != -1:
        arrData.append(strPopularity)
    else:
        arrData= add_empty_data(arrData, 1)

    if nMetaScore != -1:
        arrData.append(strMetaScore)
    else:
        arrData= add_empty_data(arrData, 1)

    #11. Genres
    genres = soup2.find("div", { "itemprop":"genre" })
    if genres is not None:
        strGenre= genres.text.replace("Genres:","").replace('|','').strip()
        strGenre = str.join("", strGenre.splitlines()).strip()
        arrData.append(strGenre)
    else:
        arrData.append(" ")

    #12. Rating
    rating = soup2.find("span", { "itemprop":"contentRating" })
    if rating is not None:
        strRating= rating.text.strip()
        strRating = str.join("", strRating).strip()
        arrData.append(strRating)
    else:
        arrData.append(" ")

    #13. Country
    if soup2.find(text="Country:") is not None:
        strCountry = soup2.find(text="Country:").findNext('a').text
        strCountry= str.join("", strCountry.splitlines()).strip()
        arrData.append(strCountry)
    else:
        arrData.append(" ")

    #14. Language
    if soup2.find(text="Language:") is not None:
        strLanguage = soup2.find(text="Language:").findNext('a').text
        strLanguage= str.join("", strLanguage.splitlines()).strip()
        arrData.append(strLanguage)
    else:
        arrData.append(" ")

    #15. Budget (outside)
    budget = soup2.find(text="Budget:")
    if budget is not None:
        strBudget= budget.parent.parent.text.replace("Budget:","").replace('|','').rstrip()
        strBudget= str.join("", strBudget.splitlines()).strip()
        arrData.append(strBudget)
    else:
        arrData.append(" ")
    #print strCountry, strLanguage, strBudget

    #16 . release dates (each countries)
    strRD= get_releaseinfo_of_movie(url2)
    arrData.append(strRD)
    
    #17. opening weekend (outside)
    openingweekend = soup2.find(text="Opening Weekend:")
    if openingweekend is not None:
        strOpeningWeekend= openingweekend.parent.parent.text.replace("Opening Weekend:","").replace('|','').rstrip()
        strOpeningWeekend = str.join("", strOpeningWeekend.splitlines()).strip()
        arrData.append(strOpeningWeekend)
    else:
        arrData.append(" ")

    #18. Gross (outside)
    gross = soup2.find(text="Gross:")
    if gross is not None:
        strGross= gross.parent.parent.text.replace("Gross:","").replace('|','').rstrip()
        strGross = str.join("", strGross.splitlines()).strip()
        arrData.append(strGross)
    else:
        arrData.append(" ")

    #19. Budget, 20. Opening Weeked, 21. Gross ,22. Week Gross, 23. Admissions, 24. Rentals, 25. FlimingDates, 26. CopyRight
    arrData = get_business_of_movie(url2, arrData)

    #27. ProductionCompany, 28. Distributors
    arrData= get_companycredits_of_movie(url2, arrData)

    #29. Runtime, 30. Color, 31. Flim Length
    techspecs= soup2.find( text="full technical specs" )
    if techspecs is None:
        add_empty_data(arrData, 3)
    else:
        if techspecs.parent['href'] is not None:
            arrData= get_techinfo_of_movie(url2, arrData)
            #print len(arrData)
        else:
            add_empty_data(arrData, 3)

    #32. Rating value
    Ratingvalue = soup2.find("span", { "itemprop":"ratingValue" })
    if Ratingvalue is None:
        add_empty_data(arrData, 1)
    else:
        strRatingvalue= Ratingvalue.text.strip()
        arrData.append(strRatingvalue)

    #33. Rating count
    Ratingcount = soup2.find("span", { "itemprop":"ratingCount" })
    if Ratingcount is None:
        add_empty_data(arrData, 1)
    else:
        strRatingcount= Ratingcount.text.strip()
        arrData.append(strRatingcount)

    arrData= get_connections(url2, arrData)

    return arrData

def check_worksheets(currServer):
    worksheets = Parsing_range.Query.all()
    todo = None
    for sheet in worksheets:
        if (sheet.status == "pend") or (sheet.status == "pending") or (sheet.status == ""):
            todo= sheet
            break
    if todo is None:
        print "There's nothing to do anymore."
        return None
    else:
        print 'Found the task.'
        return todo

def register_toServer():
    parsing= Parsing()
    all_servers = Parsing.Query.all()
    for server in all_servers:
        if CURRENT_SERVER_NAME == server.server_name:
            print "already registered."
            parsing= server
            break
        else:
            parsing = Parsing(server_name=CURRENT_SERVER_NAME, status='working', range='none', progress=0)
            parsing.save()

    return parsing


def upload_data(session, task, uri):
    try:   
        # 1. Upload file
        print "ready to open file : " + uri
        with open(uri, 'rb') as fh:
            data = fh.read()

        txtdata = File("results_"+str(task.range)+"_"+str(task.range_end), data,  "text/plain")
        txtdata.save()
        print "file has been saved."

        # 2. Attach file to rawdata object and save
        task.rawdata = txtdata
        task.status = "done"
        task.ending_time = str(datetime.now())
        task.save()
        print "file has been uploaded."
    except Exception, e:
            logging.exception(e)

def init_page(bs, task):
    nav = bs.find("div", { "class":"nav" })
    if nav is not None:
        #print nav.text'
        navitem= nav.div.findNext("div", { "class":"desc" })
        if navitem is not None:
            movies_count= re.sub("\D", "", navitem.text.split('of')[1])
            #print "real quantity : " + movies_count
            task.quantity= int(movies_count)
            task.starting_time = str(datetime.now())              
            task.save()

def get_all_movies(session, task, single_test_mode):  
    #count var
    count_total =1.0
    count_percentage= 0.0
    PAGE_MIN= 1
    PAGE_MAX= 201
    ITEMS_PER_PAGE= 50.0

    if single_test_mode is True:
        PAGE_MIN = 1
        PAGE_MAX = 2

    START_YEAR= task.range
    END_YEAR= task.range_end
    SORTS = "release_date" #release_date #num_votes
    filePath= "Output_"+str(START_YEAR)+"to"+str(END_YEAR)+".txt"

    # spliter between tasks
    text_file = open(filePath, "a")
    text_file.write("\n")
    text_file.close()

    print "Current range : " + START_YEAR + " to " + END_YEAR
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
            currError = Parsing_err(page_num=num, entity_num=idx, err_url=url)
            currError.save()
            relation= currError.relation("Parsing_range")
            relation.add(task)


    return filePath

#Here's the main
while True:
    session= register_toServer() # 1. try to register
    todo = check_worksheets(session) # 2. obtain the todo list

    if todo is None:    # 3. if no longer things to do, exit
        print "Done."
        break
    else:
        fileuri= get_all_movies(session, todo, Config.SINGLE_TEST_MODE)   # 4. if it has things to do, do work.
        if fileuri == "":
            print "There's no file."
            todo.status = "done"
            todo.save()
        else:
            upload_data(session, todo, fileuri)
