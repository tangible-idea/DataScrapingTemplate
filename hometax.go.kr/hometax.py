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
from datetime import datetime

# pip install PyInquirer
from PyInquirer import prompt, print_json

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

    countof_disabled = 0 # 선택불가항목 카운트

    checkelems = browser.find_elements_by_xpath('//div[@class="w2selectbox_native_innerDiv"]')
    for elem in checkelems:
        select1= elem.find_element_by_tag_name("select")
        if select1.get_attribute("disabled") == True:
            print("변경할 수 없는 선택항목 (면세 또는 공제 불가항목)")
            countof_disabled = countof_disabled + 1
        select2= Select(select1)
        select2.select_by_visible_text(TO_BE_CHANGED)

    clickIFclickable('trigger19',0.3)

    try:
        WebDriverWait(browser, 3).until(EC.alert_is_present())
        alert = browser.switch_to.alert
        alert.accept()
        print("alert accepted:1")
        time.sleep(0.5)
        WebDriverWait(browser, 3).until(EC.alert_is_present())
        alert = browser.switch_to.alert
        alert.accept()
        print("alert accepted:2")
    except TimeoutException:
        print("no alert")

    return countof_disabled
    

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

INQ_CONDITION = "공제대상" # 공제대상 또는 불공제대상
TO_BE_CHANGED = "불공제" # 공제 또는 불공제 
browser = None
def TryToParse(TESTorREAL):
    global browser

    print("TryToParse()")
    try:
        url = "https://www.hometax.go.kr/"
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
        clickIFclickable('rdoSearch_input_2',0.3) #분기별 옵션 선택

        select_year= browser.find_element_by_id('selectYear')
        select_qrt= browser.find_element_by_id('selectQrt')

        year_options= select_year.find_elements_by_tag_name("option")
        qrt_options= select_qrt.find_elements_by_tag_name("option")

        #메뉴만들기
        menu_list= []
        for y in year_options:
            for q in qrt_options:
                menu_list.append(INQ_CONDITION+ " 항목 조회: "+y.text+":" +q.text)
        menu_list.append("전체 아이템을 "+ TO_BE_CHANGED +" 항목으로 변경하기.")
        #menu_list.append("조회대상 수정 (현재:"+INQ_CONDITION+")")
        #menu_list.append("변경대상 수정 (현재:"+TO_BE_CHANGED+")")
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

            if('조회' in answer):
                clickIFclickable('rdoSearch_input_2', 0.3) #분기별 옵션 선택

                splited_answer= answer.split(':')
                selected_year= splited_answer[1].strip()
                selected_qrt= splited_answer[2].strip()

                ui_year= Select(select_year)
                ui_qrt= Select(select_qrt)
                ui_year.select_by_visible_text(selected_year)
                ui_qrt.select_by_visible_text(selected_qrt)

                ui_selectbox4= Select(browser.find_element_by_id('selectbox4'))
                ui_selectbox4.select_by_visible_text(INQ_CONDITION) # 불공제대상 또는 공제대상
                clickIFclickable('btnSearch',0.1)
                browser.implicitly_wait(1)
                continue

            #if('조회' in answer):

            elif('변경하기.' in answer):
                while True:
                    textof_DOM_total= browser.find_element_by_id('txtTotal').text
                    textof_DOM_totalpage= browser.find_element_by_id('txtTotalPage').text
                    total= int(textof_DOM_total)
                    totalpage= int(textof_DOM_totalpage)
                    print("총 페이지: " + str(totalpage))
                    print("총 항목개수: " + str(total))

                    if(total == 0): # 항목이 없으면 종료.
                        break

                    countof_disabled= AllClickOnThisPage()
                    print("이 페이지에서 선택불가항목: " + str(countof_disabled))
                    if(countof_disabled == total): # 더 이상 선택할 항목이 없고
                        wait = WebDriverWait(browser, 5)
                        
                    elif(countof_disabled == 10):
                        btn = wait.until(EC.element_to_be_clickable((By.ID, pglNavi_next_btn)))
                        print("다음 페이지 버튼이 있는지? " + str(btn.is_displayed()))
                        if btn.is_displayed():
                            print("다음 페이지로 넘어갑니다!")
                            clickIFclickable('pglNavi_next_btn',0.5)
                        else: # 다음 페이지 버튼도 없고 선택불가항목만 남아있으면 종료.
                            print("더 이상 선택할 항목이 없습니다!")
                            break
                continue
            else:
                exit(0)
        
    except Exception as e:
        print(e)

print("test1")
TryToParse(True)
