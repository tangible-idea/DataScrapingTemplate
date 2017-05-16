# written by python 3.6.1
#-*- coding: utf-8 -*-
from urllib.request import urlopen
import string
from bs4 import BeautifulSoup  
import logging  
logging.basicConfig(level=logging.DEBUG)

FILE_PATH = "./boxofficemojo.com/movie_data.txt"

def add_empty_data(arrData, count):
    for i in range(0,count):
        arrData.append(" ")
    return arrData

def save_to_file(filePath, arrData, countriesData=None):
    text_file = open(filePath, "a")
    for data in arrData:
        text_file.write(str(data) + "|")

    if countriesData:
        for data in countriesData:
            text_file.write(str(data) + "|")
    text_file.write('\n')
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
    td_count = 9
    if len(tables) == 4:
        #print(tables[3]) # Total lifetime grosses
        mp_boxes= tables[3].find_all("div", {"class", "mp_box_tab"})
        a= len(mp_boxes)
        for box in mp_boxes:
            if(box.text == "Total Lifetime Grosses"):
                div_content= box.findNext('div')
                trs= div_content.find_all('tr')
                for tr in trs:
                    tds= tr.find_all('td')
                    if len(tds) == 3:
                        arrData.insert(td_count, tds[1].text)
                        arrData.insert(td_count+1, tds[2].text)
                        td_count += 2
            if(box.text == "Domestic Summary"):
                print(box.findNext('div'))
            if(box.text == "The Players"):
                print(box.findNext('div'))

    return arrData


def get_movie_foreign(link, arrData):

    try:
        eachCountry = []
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
                    for idx,tr in enumerate(trs):
                        if(idx < 3): # don't save unncessary data
                            continue
                        tds= tr.find_all("td")
                        td_count = 11
                        for td in tds:
                            eachCountry.insert(td_count, td.text)
                            td_count += 1
                        save_to_file(FILE_PATH, arrData, eachCountry)
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
        if len(tabledata) == 6:
            Distributor = tabledata[0].b.getText()
            ReleaseDate = tabledata[1].b.getText()
            Genre = tabledata[2].b.getText()
            Runtime = tabledata[3].b.getText()
            Rating = tabledata[4].b.getText()
            Budget = tabledata[5].b.getText()
            arrData.extend([name , url , Distributor, ReleaseDate,Genre ,Runtime , Rating,Budget])
            add_empty_data(arrData, 1) # match gap for missing column
        elif len(tabledata) == 7:
            TotalGross = tabledata[0].b.getText()
            Distributor = tabledata[1].b.getText()
            ReleaseDate = tabledata[2].b.getText()
            Genre = tabledata[3].b.getText()
            Runtime = tabledata[4].b.getText()
            Rating = tabledata[5].b.getText()
            Budget = tabledata[6].b.getText()
            arrData.extend([ name , url , Distributor, ReleaseDate,Genre ,Runtime , Rating,Budget ,TotalGross])

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
    arrData = []

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
                            save_to_file(FILE_PATH, arrData)
                            arrData.clear()
                        counter += 1
            except Exception as e:
                logging.exception(e)

    return movies_list



get_all_movies()