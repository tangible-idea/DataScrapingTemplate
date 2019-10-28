# written in python 3.7

from time import sleep
import time
import string
import os
import re
import sys
import logging
from datetime import datetime
from datetime import timedelta

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



def printOneLine(x,y):
    print(x.strftime('%d.%b.%Y') + "    " + x.strftime('%H:%M') + "    " + y.strftime('%H:%M'))
    gap_to_next= ""

start_worktime= ""
end_worktime= ""
gap_to_next= ""
append_nexttime = False

for idx, i in enumerate(arr_final_datetime):
    #print(i)
    if start_worktime == "":
        start_worktime = i
        #print("init starting time.")

    # the last idx
    if idx == len(arr_final_datetime)-1:
        end_worktime = start_worktime + timedelta(minutes=30)
        append_nexttime = False
        printOneLine(start_worktime, end_worktime)
        start_worktime=""
        end_worktime = ""
        continue

    gap_to_next= arr_final_datetime[idx+1] - arr_final_datetime[idx]
    #print(gap_to_next)

    if gap_to_next > timedelta(minutes=75):
        if append_nexttime == True:
            end_worktime = i
        else:
            end_worktime = start_worktime + timedelta(minutes=30)

        append_nexttime = False
        printOneLine(start_worktime, end_worktime)
        start_worktime=""
        end_worktime=""
    else:
        append_nexttime = True

    
    