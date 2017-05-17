import re
import os

yes=[]
yes.reverse()
yes.extend(["","","","","","","","","","","",""])
yes.insert(0, "aaa")
yes.insert(1, "bbb")
yes.insert(10, "cccc")

for y in yes:
    print(y + "|")

print(os.getenv('username'))
sample_txt = "mstView('movie','20140561');return false;"

def extractMovieNum(txt):
    movieNum= re.sub(r'\D', "", sample_txt) # sub non-digits by regex
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

print(extractMovieNum(sample_txt))
#movieNum= re.sub(r'\D', "", sample_txt) # sub non-digits by regex