# written by python 3.*
#-*- coding: utf-8 -*-
import glob, os, sys
import codecs
from enum import Enum

class HtmlStat(Enum):
    BEFORE_THEAD = 1
    INSIDE_THEAD = 2
    AFTER_THEAD = 3

print("begin...")
# filenames
filenames = glob.glob(".\\KOBIS_download2\\*.xls")
print("completed to read all files")
with codecs.open(".\\Combined\\file.html", "w", encoding='utf-8', errors='ignore') as outfile:
    for fidx, fname in enumerate(filenames):
        #print("current file name : " + str(fname.encode("cp949")))
        with codecs.open(fname, "r", encoding='utf-8', errors='ignore') as infile:
        #with open(fname) as infile:
            print( str(fidx) +" out of "+ str(len(filenames)))
            status= HtmlStat.BEFORE_THEAD
            caption = ""
            for line in infile:
                if "<html>" in line:
                    continue
                if "<head>" in line:
                    continue
                if "<title>" in line:
                    continue
                if "<meta " in line:
                    continue
                if "</head>" in line:
                    continue
                if "<body>" in line:
                    continue
                if "</body>" in line:
                    continue
                if "</html>" in line:
                    continue
                if "<caption>" in line:
                    arr = line.split("'")
                    if len(arr) != 0:
                        caption= arr[1].strip()
                        #print(caption)
                    continue
                if "<thead>" in line:
                    status= HtmlStat.INSIDE_THEAD
                    continue
                elif "</thead>" in line:
                    status= HtmlStat.AFTER_THEAD
                    continue
                if status is HtmlStat.INSIDE_THEAD: # don't write all contents of thead
                    continue
                if status is HtmlStat.AFTER_THEAD: # add custom td
                    if "<tr>" in line:
                        line += u"\t\t<td>"+caption+ u"</td>\r\n"
                        
                outfile.write(line)
                #print(line)
print ('done')