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

arr_final_datetime= []
for i in range(len(arr_datetime)-1, 0, -1):
    factor5= arr_datetime[i].minute % 5
    replaced= arr_datetime[i].replace(minute=(arr_datetime[i].minute-factor5))
    #print(str(replaced))
    arr_final_datetime.append(replaced)


def endloop(x):
    prev_dt= x
    print(x)

start_worktime= ""
end_worktime= ""
prev_dt= ""
for i in arr_final_datetime:
    if prev_dt != "":
        timediff_withprev= start_worktime - prev_dt
    #test= arr_datetime[i-1] - arr_datetime[i]
    #print(str(arr_datetime[i]) + " - " + str(arr_datetime[i-1]) + " = " + str(test) + ", " + str(test.seconds))
    if start_worktime == "":
        start_worktime= i
        endloop(i)
        continue

    # if end_worktime == "":
    #     end_worktime= arr_datetime[i]
    #     continue 
    
    endloop(i)
    
    