#-*- coding: utf-8 -*-
#import pandas as pd
import glob, os, sys
#import xlrd
import codecs

print("begin...")
# filenames
filenames = glob.glob(".\\KOBIS_download2\\*.xls")
print("completed to read all files")
with codecs.open(".\\Combined\\file.html", "w",encoding='utf-8', errors='ignore') as outfile:
    for fname in filenames:
        print("current file name : " + fname)
        with codecs.open(fname, "r",encoding='utf-8', errors='ignore') as infile:
        #with open(fname) as infile:
            for line in infile:
                if "<html>" in line:
                    continue
                if "<head>" in line:
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
                outfile.write(line)
                #print(line)
print ('done')