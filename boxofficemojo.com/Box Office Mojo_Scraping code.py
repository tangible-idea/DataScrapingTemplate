from urllib.request import urlopen
import string
from bs4 import BeautifulSoup  
import logging  
logging.basicConfig(level=logging.DEBUG)

def add_empty_data(arrData, count):
    for i in range(0,count):
        arrData.append(" ")
    return arrData

def save_to_file(filePath, arrData):
    text_file = open(filePath, "a")
    for data in arrData:
        text_file.write(str(data) + "|")
    #text_file.write(str(data))
    text_file.write('\n')
    text_file.close()

def get_movie_foreign(link, arrData):

    try:
        each_column=""
        url = "http://www.boxofficemojo.com"+ link + "&page=intl"
        page = urlopen(url)
        soup = BeautifulSoup(page, "lxml")

        contents= soup.find('table', attrs={'border': '3' , 'cellspacing':'0', 'cellpadding':'5', 'align':'center', 'style':'margin-top: 5px;'})
        if len(contents) == 1:
            print(contents)
            intl_table= contents.tr.td.table
            if intl_table:
                trs= intl_table.find_all("tr")
                if len(trs) == 3:
                    print ("no data")
                else:
                    for tbl in intl_table:
                        arrData.append(tbl.text)
        return arrData
    except Exception as e:
        logging.exception(e)
        return arrData

def get_movie_detail(movies_list, link, arrData):

    #result= ""
    if link not in movies_list:
        #print link + '|' +  studio# + '|' + gross + '|' + gross_th+ '|' + opening + '|' + opening_th+ '|' + opendate
        #print link
        movies_list.append(link)

        url = "http://www.boxofficemojo.com"+ link
        page = urlopen(url)
        soup = BeautifulSoup(page, "lxml")
        #contents = soup.find(id="body").find("table").find("table").find("table").find("table").find_all("td")
        #print soup.find(id="body").find_all("table")[1]
        contents= soup.find('table', attrs={'border': '0' , 'cellspacing':'1', 'cellpadding':'4' , 'bgcolor':'#dcdcdc', 'width':'95%'})
        tabledata= contents.find_all("td")

        name_table= soup.find('table', attrs={'border': '0' , 'cellspacing':'0', 'cellpadding':'0' , 'width':'100%', 'style':'padding-top: 5px;'})
        name= name_table.font.b.getText()
        #print name
        
        if len(tabledata) == 6:
            Distributor= tabledata[0].b.getText()
            ReleaseDate= tabledata[1].b.getText()
            Genre = tabledata[2].b.getText()
            Runtime= tabledata[3].b.getText()
            Rating = tabledata[4].b.getText()
            Budget = tabledata[5].b.getText()
            arrData.extend([name , url , Distributor, ReleaseDate,Genre ,Runtime , Rating,Budget])
        elif len(tabledata) == 7:
            TotalGross = tabledata[0].b.getText()
            Distributor= tabledata[1].b.getText()
            ReleaseDate= tabledata[2].b.getText()
            Genre = tabledata[3].b.getText()
            Runtime= tabledata[4].b.getText()
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
                            arrData= get_movie_detail(movies_list, link, arrData) 
                            arrData= get_movie_foreign(link, arrData)
                            save_to_file("./boxofficemojo.com/movie_data.txt", arrData)
                        counter += 1
            except Exception as e:
                logging.exception(e)

    return movies_list



get_all_movies()