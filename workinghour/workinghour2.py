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
  	print(x.strip())

history_thismonth = []
for item in history_list:
    #text= str(item)
    print(item)
    if "October" in item:
       history_thismonth.append(item)
       #print(item)

for t in history_thismonth:
    t = t + ", 2019"
    datetime_object = datetime.strptime(t, "%B %d, %I:%M %p, %Y")
    print(datetime_object)