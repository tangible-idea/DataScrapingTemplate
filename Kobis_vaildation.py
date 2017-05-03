# written by python 2.*
#-*- coding: utf-8 -*-
import glob, os, sys
reload(sys)
sys.setdefaultencoding('utf-8')

#print os.getenv('username')
PATH = "C:\\Users\\fanta\\Documents\\Movie_DataMiner\\KOBIS_download2"
MAX_PAGE = -1
MAX_NUM = -1
arrFile= []
arrNums= []
arrPages= []

class FileInfoPair():
    num= 0
    page= 0

    def __init__(self, num, page):
        self.num = num
        self.page= page


def validation():
    temp= -1
    for file in os.listdir(PATH):
        if file.endswith(".xls"):
            file= file.replace(".xls","")
            arr= file.rsplit("_")
            file_num= arr[len(arr)-1]
            file_page= arr[len(arr)-2]
            #print "num : " + file_num +", " + "page : " + file_page
            arrFile.append(FileInfoPair(int(file_num), int(file_page)))
            arrPages.append(int(file_page))
            arrNums.append(int(file_num))

def search():
    for file in arrFile:
        file.num

validation()
arrPages.sort()
arrNums.sort()

for x in range(0,9):
    print arrNums.count(x)
