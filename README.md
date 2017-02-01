# DataMiner

##What is this for?
It comprises One WPF C# app + One python script
Firstly, for the python script, you can run this script at any isolated server.
During parsing the data, manager or data administrator can monitor what's going on data mining(or scraping) server via the C# application.

##What data you can scrap?
For this project. It's for scrapping IMDB.com website. it can be mining every feature movie's data.
For now, it supports 34 columns.
1. Movie Name
2. Link
3. Director
4. Writers
5. Stars
6. Nomination
7. Reviews
8. Critics
9. Popularity 
11. Genres
12. Rating
13. Country
14. Language
15. Budget (outside)
16. release dates (each country)
17. opening weekend (outside)
18. Gross (outside)
19. Budget
20. Opening Weekend
21. Gross
22. Week Gross
23. Admissions
24. Rentals
25. FlimingDates
26. CopyRight
27. ProductionCompany
28. Distributors
29. Runtime
30. Color
31. Film Length
32. Rating value
33. Rating count
34. connections
For further information, please refer to comments of a python script.

##Installation
------------
* BeautifulSoup4
Clone this repository:

    pip install git+https://github.com/milesrichardson/ParsePy.git
or manually download the package from here : 
https://pypi.python.org/pypi/beautifulsoup4

* lxml 3.6.4
Download the packpage here : 
    https://pypi.python.org/pypi/lxml/3.6.4)

* ParsePy (https://github.com/milesrichardson/ParsePy)
The easiest way to install this package is by downloading or
cloning this repository:

    pip install git+https://github.com/milesrichardson/ParsePy.git
    
##Introduction
I wrote about this project more than 50 commits at TFS privately.
Meanwhile, I thought it might be useful to make it public for people who like data mining.
I've begun for scripting python with this project and data mining as well.
Thank you.
