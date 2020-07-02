![C#](https://img.shields.io/badge/C%23-.net4.5-blue.svg)
![python](https://img.shields.io/badge/python-2.x-blue.svg)
![python](https://img.shields.io/badge/python-3.x-blue.svg)
![licence](https://img.shields.io/badge/License-Apache2.0-green.svg)

# DataMiner
==========

What data you can scrap?
------------
Any website scraping codes can be added to this project for researching purpose(or similar). 
Currently, this project supports following sites. For further information, please refer to comments in python scripts.
* imdb.com
Dependency : BeautifulSoup4, lxml, ParsePy
* kobis.or.kr
Dependency : BeautifulSoup4, lxml, Selenium
* boxofficemojo.com
Dependency : BeautifulSoup4, lxml
* hometax.go.kr
Dependency : selenium, PyInquirer

IMDB.com project
------------
It comprises One WPF C# app + One python script.
Firstly, for the python script, you can run this script at any isolated server.
During parsing the data, manager or data administrator can monitor what is going on the data mining(or scraping) server via the C# application.

Hometax project
------------
Manipulations of select tag alert control.
   
```
Installation
------------
* BeautifulSoup4
Clone this repository:

    pip install BeautifulSoup4
or manually download the package from here : 
https://pypi.python.org/pypi/beautifulsoup4

* lxml 3.6.4 or higher
Clone this repository:
```
    yum install libxslt-devel libxml2-devel
```
Download the packpage here : 
    https://pypi.python.org/pypi/lxml/3.6.4)

* ParsePy (https://github.com/milesrichardson/ParsePy)
The easiest way to install this package is by downloading or
cloning this repository:
```
    pip install git+https://github.com/milesrichardson/ParsePy.git
```

* Selenium
```
   pip install selenium
```
* PyInquirer
```
    pip instsall PyInquirer
    
Introduction
------------
