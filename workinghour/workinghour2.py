# written in python 3.7

from time import sleep
import time
import string
import os
import re
import sys
import logging
from datetime import datetime

history_list = []
f = open("versions.txt","r")  
for x in f:
  if x.strip() == "":
  	continue
  elif "current" in x.strip():
  	continue
  else:
  	history_list.append(x.strip())
  	#print(x.strip())

history_thismonth = []
for item in history_list:
    #text= str(item)
    #print(item)
    if "October" in item:
       history_thismonth.append(item)
       #print(item)

history_thismonth_redundant = list(dict.fromkeys(history_thismonth))

arr_datetime = []
prev_datetime = ""
for t in history_thismonth_redundant:
    t = t + ", 2019"
    prev_datetime
    datetime_object = datetime.strptime(t, "%B %d, %I:%M %p, %Y")
    #print(datetime_object)
    arr_datetime.append(datetime_object)


for i in range(len(arr_datetime)-1, 0, -1):
	test= arr_datetime[i-1] - arr_datetime[i]
	print(str(arr_datetime[i-1]) + " - " + str(arr_datetime[i]) + " = " + str(test))