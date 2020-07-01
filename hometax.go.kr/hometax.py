# written in python 3.7
#-*- coding: utf-8 -*-
#import urllib2  
# import urllib.request
# import urllib.error
# import urllib.parse
from threading import Timer
from time import sleep
import time
import string
import os
import re
import sys
import logging
from datetime import datetime
from PyInquirer import prompt, print_json

# pip install BeautifulSoup4
# pip install lxml
from bs4 import BeautifulSoup

# pip install selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
import ssl

#def BSoup():
#    html = browser.page_source
#            print(html)
#            soup = BeautifulSoup(html, "html.parser")
#            print(soup)
#            test= soup.find_all("div", {'class':'w2selectbox_native_innerDiv'})
#            print(test)
#            for div in test: 
#                options= div.select.find(text="불공제")
#                options.decompose()


def AllClickOnThisPage():
    global browser
    allcheck= browser.find_element_by_xpath('//input[@title="전체선택"]')
    allcheck.click()

    checkelems = browser.find_elements_by_xpath('//div[@class="w2selectbox_native_innerDiv"]')
    for elem in checkelems:
        select1= elem.find_element_by_tag_name("select")
        select2= Select(select1)
        select2.select_by_visible_text('공제')

    clickIFclickable('trigger19',0.3)

    try:
        WebDriverWait(browser, 3).until(EC.alert_is_present())
        alert = browser.switch_to.alert
        alert.accept()
        print("alert accepted")
    except TimeoutException:
        print("no alert")

    

def clickIFclickable(id, waittime=3):
    global browser
    #print(id)
    try:
        wait = WebDriverWait(browser, 10)
        btn = wait.until(EC.element_to_be_clickable((By.ID, id)))
        print("Element is visible? " + str(btn.is_displayed()))
        print(btn.text + "is clickable.")
        time.sleep(waittime)
        btn.click()
        time.sleep(waittime)
    except Exception as e:
        print(e)
        print('try another way')

        browser.find_element_by_id(id).click()
        time.sleep(waittime)

def hoverIFpresented(id):
    global browser
    wait = WebDriverWait(browser, 10)
    btn = wait.until(EC.element_to_be_clickable((By.ID, id)))
    hover = ActionChains(browser).move_to_element(btn)
    hover.perform()

browser = None
def TryToParse(TESTorREAL):
    global browser

    print("TryToParse()")
    try:
        url = "https://www.hometax.go.kr/"
        #url = "https://www.hometax.go.kr/websquare/websquare.wq?w2xPath=/ui/pp/index_pp.xml"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("window-size=1400x600")
        chrome_options.add_argument("--disable-popup-blocking");
        browser = webdriver.Chrome(options=chrome_options)
        browser.implicitly_wait(1)  # seconds
        
        browser.get(url)
        print(browser.title)

        clickIFclickable('textbox81212912',2)
        while True:
            try:
                #btn_new= browser.find_element_by_css_selector('#textbox915')
                btn_new= browser.find_element_by_css_selector('#textbox81212912')
                if(btn_new.text == "로그아웃"):
                    print("로그인됨.")
                    break
                time.sleep(1)
            except Exception as e:
                #if "no such element" in e:
                if(e.__class__ is NoSuchElementException):
                    print("홈택스 로그인 해주세요.")
                pass
        
        browser.get("https://hometax.go.kr/websquare/websquare.wq?w2xPath=/ui/pp/index_pp.xml&tmIdx=1&tm2lIdx=0105040000&tm3lIdx=0105040400")

        time.sleep(0.5)
        #browser.switch_to_frame(browser.find_element_by_xpath('//iframe[@src="https://tecr.hometax.go.kr/websquare/websquare.html?w2xPath=/ui/cr/c/b/UTECRCB023.xml"]'))
        browser.switch_to_frame(browser.find_element_by_xpath('//iframe[@id="txppIframe"]'))

        time.sleep(1.5)
        clickIFclickable('rdoSearch_input_2',0.3)

        select_year= browser.find_element_by_id('selectYear')
        select_qrt= browser.find_element_by_id('selectQrt')

        year_options= select_year.find_elements_by_tag_name("option")
        qrt_options= select_qrt.find_elements_by_tag_name("option")

        #메뉴만들기
        menu_list= []
        for y in year_options:
            for q in qrt_options:
                menu_list.append("불공제항목 조회: "+y.text+":" +q.text)
        menu_list.append("전체체크 시작.")
        menu_list.append("종료.")

        while(True):
            questions = [
                {
                    'type': 'list',
                    'name': 'menu',
                    'message': '무엇을 도와드릴까요?',
                    'choices': menu_list
                }]
            answer = prompt(questions)["menu"]

            if('불공제항목 조회' in answer):
                splited_answer= answer.split(':')
                selected_year= splited_answer[1].strip()
                selected_qrt= splited_answer[2].strip()

                ui_year= Select(select_year)
                ui_qrt= Select(select_qrt)
                ui_year.select_by_visible_text(selected_year)
                ui_qrt.select_by_visible_text(selected_qrt)

                ui_selectbox4= Select(browser.find_element_by_id('selectbox4'))
                ui_selectbox4.select_by_visible_text('불공제대상')
                clickIFclickable('btnSearch',0.1)
                browser.implicitly_wait(1)
                continue

            elif(answer == '전체체크 시작.'):
                DOM_totalpage= browser.find_element_by_id('txtTotalPage')
                textof_DOM_totalpage= DOM_totalpage.text
                totalpage= int(textof_DOM_totalpage)
                print("총 페이지 수: " + str(totalpage))
                if totalpage <= 10:
                    for x in range(1,totalpage):
                        clickIFclickable("pglNavi_page_"+str(x))
                        AllClickOnThisPage()
                else: # 10페이지 이상 남았을 경우:
                    for x in range(1,11):
                        clickIFclickable("pglNavi_page_"+str(x))
                        AllClickOnThisPage()
                        totalpage = totalpage - 10
                        if x == 10:
                            clickIFclickable('pglNavi_next_btn',0.5)
                continue
            else:
                exit(0)
        
    except Exception as e:
        print(e)

print("test1")
TryToParse(True)
