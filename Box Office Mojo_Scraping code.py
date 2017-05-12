from urllib.request import urlopen
import string
from bs4 import BeautifulSoup  
import logging  
logging.basicConfig(level=logging.DEBUG)



def get_all_movies():  
    """ returns all the movie urls from boxofficemojo.com in a list"""

    # Alphabet loop for how movies are indexed including
    # movies that start with a special character or number
    index = ["NUM"] + list(string.ascii_uppercase)

    # List of movie urls
    movies_list = []

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

                            # next_td_tag = row.td.findNext('td')
                            # studio = next_td_tag.font.contents[0]

                            # next_td_tag = row.td.findNext('td').findNext('td')
                            # gross = next_td_tag.font.contents[0]

                            # next_td_tag = row.td.findNext('td').findNext('td').findNext('td')
                            # gross_th = next_td_tag.font.contents[0]

                            # next_td_tag = row.td.findNext('td').findNext('td').findNext('td').findNext('td')
                            # opening = next_td_tag.font.contents[0]

                            # next_td_tag = row.td.findNext('td').findNext('td').findNext('td').findNext('td').findNext('td')
                            # opening_th = next_td_tag.font.contents[0]

                            # next_td_tag = row.td.findNext('td').findNext('td').findNext('td').findNext('td').findNext('td').findNext('td')                            
                            # if next_td_tag.font.a is not NoneType:
                            #     opendate = next_td_tag.font.a.getText()

                            

                            if link not in movies_list:
                                #print link + '|' +  studio# + '|' + gross + '|' + gross_th+ '|' + opening + '|' + opening_th+ '|' + opendate
                                #print link
                                movies_list.append(link)

                                url2 = "http://www.boxofficemojo.com"+ link
                                page2 = urlopen(url2)
                                soup2 = BeautifulSoup(page2, "lxml")
                                #contents2 = soup2.find(id="body").find("table").find("table").find("table").find("table").find_all("td")
                                #print soup2.find(id="body").find_all("table")[1]
                                contents2= soup2.find('table', attrs={'border': '0' , 'cellspacing':'1', 'cellpadding':'4' , 'bgcolor':'#dcdcdc', 'width':'95%'})
                                tabledata2= contents2.find_all("td")

                                name_table2= soup2.find('table', attrs={'border': '0' , 'cellspacing':'0', 'cellpadding':'0' , 'width':'100%', 'style':'padding-top: 5px;'})
                                name2= name_table2.font.b.getText()
                                #print name2
                                
                                if len(tabledata2) == 6:
                                    Distributor= tabledata2[0].b.getText()
                                    ReleaseDate= tabledata2[1].b.getText()
                                    Genre = tabledata2[2].b.getText()
                                    Runtime= tabledata2[3].b.getText()
                                    Rating = tabledata2[4].b.getText()
                                    Budget = tabledata2[5].b.getText()
                                    print(name2 +'|'+ url2 +'|'+ Distributor+'|'+ ReleaseDate+'|'+Genre +'|'+Runtime +'|'+ Rating+'|'+Budget)
                                elif len(tabledata2) == 7:
                                    TotalGross = tabledata2[0].b.getText()
                                    Distributor= tabledata2[1].b.getText()
                                    ReleaseDate= tabledata2[2].b.getText()
                                    Genre = tabledata2[3].b.getText()
                                    Runtime= tabledata2[4].b.getText()
                                    Rating = tabledata2[5].b.getText()
                                    Budget = tabledata2[6].b.getText()
                                    print(name2 +'|'+ url2 +'|'+ Distributor+'|'+ ReleaseDate+'|'+Genre +'|'+Runtime +'|'+ Rating+'|'+Budget +'|'+TotalGross)


                                #print contents2[0]

                        counter += 1
            except Exception as e:
                logging.exception(e)

    return movies_list



get_all_movies()