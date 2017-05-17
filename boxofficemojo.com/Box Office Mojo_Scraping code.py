# written by python 3.6.1
#-*- coding: utf-8 -*-
from urllib.request import urlopen
import json
import string
import re
from bs4 import BeautifulSoup  
import logging  
logging.basicConfig(level=logging.DEBUG)

FILE_PATH = "./boxofficemojo.com/movie_data.txt"

def add_empty_data(arrData, count):
    for i in range(0,count):
        arrData.append(" ")
    return arrData

def remove_special_chars(dictData):
    
    for key in dictData:
        new_key= re.sub(r'\W+', '', key)
        dictData[new_key] = dictData.pop(key)
    return dictData

def save_to_json(filePath, dictData, countriesData=None):
    
    dictData = remove_special_chars(dictData)
    countriesData = remove_special_chars(countriesData)
    
    if countriesData:
        merged = dict(dictData)
        merged.update(countriesData)
        dictData = merged

    with open(filePath, "a") as outfile:
        json.dump(dictData, outfile, ensure_ascii=False)


def save_to_file(filePath, dictData, countriesData=None):
    
    dictData = remove_special_chars(dictData)
    countriesData = remove_special_chars(countriesData)
    
    if countriesData:
        merged = dict(dictData)
        merged.update(countriesData)
        dictData = merged

    Arranged= []
    add_empty_data(Arranged, 50)

    Keys = ["Name", "URL", "Genre","Runtime", "Rating", "MovieRanking"
    , "PercentageofTotalGross", "WidestRelease", "CloseDate", "InRelease", "TotalGross"
    , "Distributor", "ReleaseDate", "Budget", "Domestic_Gross", "Domestic_Percentage"
    , "Foreign_Gross", "Foreign_Percentage", "Worldwide_Gross", "OpeningWeekend"
    , "Countryclicktoviewweekendbreakdown", "Dist", "ReleaseDate", "ReleaseDate"
    , "OpeningWknd", "% ofTotal", "Total Gross ", " As Of"]

    # Write a header
    for header in Keys:
        text_file.write((header + u"|").encode('utf-8'))
    text_file.write("\n".encode('utf-8'))
        
    text_file = open(filePath, "ab")
    for key, value in sorted(dictData.items()):
        for i ,k in enumerate(Keys):
            if key == k:
                Arranged.insert(i, value)
        
    for data in Arranged:
        text_file.write((data + u"|").encode('utf-8'))

    text_file.write("\n".encode('utf-8'))
    text_file.close()
 
def get_total_lifetime_grosses(link, arrData):
    
    url = "http://www.boxofficemojo.com"+ link
    page = urlopen(url)
    soup = BeautifulSoup(page, "lxml")

    #div_body= soup.find("div", {"id", "body"})
    #main_tbl= div_body.table.findNext('table').tbody.tr.td.table

    #print(main_tbl)
    tables = soup.find_all('table', attrs={'border': '0' , 'cellspacing':'0', 'cellpadding':'0' , 'width':'100%'})
    
    print( len(tables))
    #td_count = 9
    if len(tables) == 4:
        #print(tables[3]) # Total lifetime grosses
        mp_boxes= tables[3].find_all("div", {"class", "mp_box_tab"})
        a= len(mp_boxes)
        for box in mp_boxes:
            if(box.text == "Total Lifetime Grosses"):
                div_content= box.findNext('div')
                trs = div_content.find_all('tr')
                for tr in trs:
                    tds = tr.find_all('td')
                    if len(tds) == 3:
                        arrData[tds[0].text.strip()+"_Gross"] = tds[1].text.strip()
                        arrData[tds[0].text.strip()+"_Percentage"] = tds[2].text.strip()
                        
            if(box.text == "Domestic Summary"):
                div_content = box.findNext('div')
                DS_tables = div_content.find_all('table', attrs = { 'border': '0' , 'cellspacing':'0', 'cellpadding':'0'})
                for DS_table in DS_tables:
                    DS_trs = DS_table.find_all('tr')
                    for DS_tr in DS_trs:
                        DS_tr_title = DS_tr.td.text.strip()
                        if(DS_tr_title == "Opening\xa0Weekend:") or (DS_tr_title == "Opening Weekend:"):
                            DS_tr_content = DS_tr.td.findNext('td')
                            if DS_tr_content:
                                arrData["Opening Weekend"] = DS_tr_content.text.strip()
                                
                        elif "(#" in DS_tr_title:
                            arrData['Movie Ranking'] = DS_tr_title

                        elif "%\xa0of\xa0Total\xa0Gross" in DS_tr_title or "% of Total Gross" in DS_tr_title:
                            DS_tr_content = DS_tr.td.findNext('td')
                            if DS_tr_content:
                                arrData['Percentage of Total Gross'] = DS_tr_content.text.strip()

                        elif DS_tr_title == "Widest\xa0Release:" or DS_tr_title == "Widest Release:":
                            DS_tr_content = DS_tr.td.findNext('td')
                            if DS_tr_content:
                                arrData['Widest Release'] = DS_tr_content.text.strip() # 14.

                        elif DS_tr_title == "Close\xa0Date:" or DS_tr_title == "Close Date:":
                            DS_tr_content = DS_tr.td.findNext('td')
                            if DS_tr_content:
                                arrData['Close Date'] = DS_tr_content.text.strip() # 15.

                        elif DS_tr_title == "In\xa0Release:" or DS_tr_title == "In Release:":
                            DS_tr_content = DS_tr.td.findNext('td')
                            if DS_tr_content:
                                arrData['In Release'] = DS_tr_content.text.strip() # 15.
                            
                        
            if(box.text == "The Players"):
                #print(box.findNext('div'))
                pass

    return arrData


def get_movie_foreign(link, arrData):

    try:
        eachCountry = {}
        ColumnHeaders= []
        url = "http://www.boxofficemojo.com"+ link + "&page=intl"
        page = urlopen(url)
        soup = BeautifulSoup(page, "lxml")

        contents = soup.find('table', attrs={'border': '3' , 'cellspacing':'0', 'cellpadding':'5', 'align':'center', 'style':'margin-top: 5px;'})
        if len(contents) == 1:
            #print(contents)
            intl_table = contents.tr.td.table
            if intl_table:
                trs = intl_table.find_all("tr")
                if len(trs) == 3:
                    print ("no data")
                else:
                    for row,tr in enumerate(trs):
                        if row == 0:
                            tds= tr.find_all("td") # get each header's text
                            for td in tds:
                                header= td.text.strip()
                                if "/" in header:
                                    divided_header = header.split('/')
                                    ColumnHeaders.append(divided_header[0])
                                    ColumnHeaders.append(divided_header[1])
                                else:
                                    ColumnHeaders.append(td.text.strip()) 
                        if(row < 3): # don't save unncessary data
                            continue
                        tds= tr.find_all("td")
                        for column, td in enumerate(tds):
                            # 11. Country, 12.Dist, 13. Release Date, 14.OW, 15.% of Total, 16.Total gross, 17. as of
                            eachCountry[ColumnHeaders[column]] = td.text.strip()
                        save_to_file(FILE_PATH, arrData, eachCountry)
                        #save_to_json(FILE_PATH, arrData, eachCountry)
                        eachCountry.clear()
        return arrData
    except Exception as e:
        logging.exception(e)
        return arrData

def get_movie_detail(movies_list, link, arrData):

    if link not in movies_list:
        movies_list.append(link)

        url = "http://www.boxofficemojo.com"+ link # 1. URL
        page = urlopen(url)
        soup = BeautifulSoup(page, "lxml")
        contents= soup.find('table', attrs={'border': '0' , 'cellspacing':'1', 'cellpadding':'4' , 'bgcolor':'#dcdcdc', 'width':'95%'})
        tabledata = contents.find_all("td")

        name_table = soup.find('table', attrs={'border': '0' , 'cellspacing':'0', 'cellpadding':'0' , 'width':'100%', 'style':'padding-top: 5px;'})
        name = name_table.font.b.getText() # 0. Name
        
        # 2. Distributor, 3. Release Date, 4. Genre, 5. Runtime, 6. Rating, 7. Budget, 8. TotalGross
        arrData['Name'] = name
        arrData['URL'] = url
        if len(tabledata) == 6:
            Distributor = tabledata[0].b.getText()
            ReleaseDate = tabledata[1].b.getText()
            Genre = tabledata[2].b.getText()
            Runtime = tabledata[3].b.getText()
            Rating = tabledata[4].b.getText()
            Budget = tabledata[5].b.getText()

            arrData['Distributor'] = Distributor
            arrData['ReleaseDate'] = ReleaseDate
            arrData['Genre'] = Genre
            arrData['Runtime'] = Runtime
            arrData['Rating'] = Rating
            arrData['Budget'] = Budget
            
            #arrData.extend([name , url , Distributor, ReleaseDate,Genre ,Runtime , Rating,Budget])
            #add_empty_data(arrData, 1) # match gap for missing column
        elif len(tabledata) == 7:
            TotalGross = tabledata[0].b.getText()
            Distributor = tabledata[1].b.getText()
            ReleaseDate = tabledata[2].b.getText()
            Genre = tabledata[3].b.getText()
            Runtime = tabledata[4].b.getText()
            Rating = tabledata[5].b.getText()
            Budget = tabledata[6].b.getText()

            arrData['TotalGross'] = TotalGross
            arrData['Distributor'] = Distributor
            arrData['ReleaseDate'] = ReleaseDate
            arrData['Genre'] = Genre
            arrData['Runtime'] = Runtime
            arrData['Rating'] = Rating
            arrData['Budget'] = Budget
            #arrData.extend([ name , url , Distributor, ReleaseDate,Genre ,Runtime , Rating,Budget ,TotalGross])

            #print (result)
            

        #print contents2[0]
    return arrData
        
def get_all_movies():  
    """ returns all the movie urls from boxofficemojo.com in a list"""

    # Alphabet loop for how movies are indexed including
    # movies that start with a special character or number
    index = ["NUM"] + list(string.ascii_uppercase)

    # List of movie urls
    movies_list = []

    # data
    arrData = {'arrData' : 0}

    # Loop through the pages for each letter
    for letter in index:

        # Loop through the pages within each letter
        for num in range(1, 20):
            url = ("http://www.boxofficemojo.com/movies/alphabetical.htm?"
                   "letter=" + letter + "&page=" + str(num))
            try:
                page = urlopen(url)
                soup = BeautifulSoup(page, "lxml")
                rows = soup.find(id="body").find("table").find("table").find_all(
                    "table")[1].find_all("tr")

                # skip index row
                if len(rows) > 1:
                    counter = 1
                    for row in rows:

                        # skip index row
                        if counter > 1:
                            link = row.td.font.a['href']
                            arrData = get_movie_detail(movies_list, link, arrData) 
                            arrData = get_total_lifetime_grosses(link, arrData)
                            arrData = get_movie_foreign(link, arrData)
                            #save_to_file(FILE_PATH, arrData)
                            arrData.clear()
                        counter += 1
            except Exception as e:
                logging.exception(e)

    return movies_list



get_all_movies()