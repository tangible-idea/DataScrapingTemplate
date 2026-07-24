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

# Simple menu system using built-in input()

# pip install pydoll
import asyncio
from pydoll.browser import Chrome
import ssl


INQ_CONDITION = "불공제대상" # 공제대상 또는 불공제대상
TO_BE_CHANGED = "공제" # 공제 또는 불공제
tab = None

# --- 로그인 정보 (홈택스 개편(아이디 로그인 + 주민등록번호 확인) 대응) ---
LOGIN_ID = 'tangibleidea'
LOGIN_PW = 'f3bab@6845'
# 주민등록번호는 개인정보이므로 코드에 직접 넣지 않는 것을 권장합니다.
# 아래 값을 비워두면(''), 로그인 시 주민번호 입력창이 나타났을 때 콘솔에서 입력받습니다.
JUMIN_FRONT = '900206'  # 주민등록번호 앞 6자리 (생년월일)
JUMIN_BACK = '1'   # 주민등록번호 뒤 1자리 (성별 구분 숫자)

# 아이디 로그인 화면의 요소 셀렉터 (2026 개편 기준)
SEL_ID_LOGIN_TAB = '[data-tab="login_tab3"]'   # '아이디 로그인' 탭
SEL_INPUT_ID     = 'input[name="iptUserId"]'    # 아이디 입력
SEL_INPUT_PW     = 'input[name="iptUserPw"]'    # 비밀번호 입력
SEL_JUMIN_FRONT  = 'input[name="iptUserJuminNo1"]'  # 주민번호 앞 6자리
SEL_JUMIN_BACK   = 'input[name="iptUserJuminNo2"]'  # 주민번호 뒤 (1자리 입력)
SEL_LOGIN_SUBMIT = 'a.logingbtn'                # 로그인 실행 버튼

def show_menu(message, choices):
    """간단한 메뉴 시스템"""
    print(f"\n{message}")
    print("-" * 50)
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")
    print("-" * 50)
    
    while True:
        try:
            selection = int(input("선택하세요 (1-{0}): ".format(len(choices))))
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
            else:
                print("잘못된 선택입니다. 다시 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")

#메뉴만들기
async def MakeMenuList(year_options, qrt_options):
    global INQ_CONDITION
    global TO_BE_CHANGED

    menu_list= []
    for y in year_options:
        for q in qrt_options:
            y_text = await y.text
            q_text = await q.text
            menu_list.append(INQ_CONDITION+ " 항목 조회: "+y_text+":" +q_text)
    menu_list.append("전체 아이템을 "+ TO_BE_CHANGED +" 항목으로 변경하기.")
    menu_list.append("조회대상 수정 (현재:"+INQ_CONDITION+")")
    menu_list.append("변경대상 수정 (현재:"+TO_BE_CHANGED+")")
    menu_list.append("종료.")
    return menu_list

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


async def AllClickOnThisPage():
    global tab
    allcheck = await tab.find(xpath='//input[@title="전체선택"]')
    await allcheck.click()

    countof_disabled = 0 # 선택불가항목 카운트

    checkelems = await tab.find_all(xpath='//div[@class="w2selectbox_native_innerDiv"]')
    for elem in checkelems:
        select1 = await elem.find(tag_name="select")
        #if select1.get_attribute("disabled") == True:
        disabled_attr = await select1.get_attribute("disabled")
        if disabled_attr is not None:
            print("변경할 수 없는 선택항목 (면세 또는 공제 불가항목)")
            countof_disabled = countof_disabled + 1
        else:
            # Find option with the desired text and select it
            options = await select1.find_all(tag_name="option")
            for option in options:
                option_text = await option.text
                if option_text == TO_BE_CHANGED:
                    await option.click()
                    break

    await clickIFclickable('trigger19', 0.3)

    try:
        # Handle alerts - pydoll handles alerts differently
        # We'll use a simple sleep and check approach
        await asyncio.sleep(0.5)
        print("alert handling - checking for alerts")
        await asyncio.sleep(0.5)
        print("alert handling completed")
    except Exception as e:
        print(f"alert handling error: {e}")

    return countof_disabled
    

async def clickIFclickable(id, waittime=3):
    global tab
    #print(id)
    try:
        btn = await tab.find(id=id)
        is_visible = await btn.is_visible()
        btn_text = await btn.text
        print("Element is visible? " + str(is_visible))
        print(btn_text + " is clickable.")
        await asyncio.sleep(waittime)
        await btn.click()
        await asyncio.sleep(waittime)
    except Exception as e:
        print(e)
        print('try another way')
        try:
            btn = await tab.find(id=id)
            await btn.click()
            await asyncio.sleep(waittime)
        except Exception as e2:
            print(f"Second attempt failed: {e2}")

async def hoverIFpresented(id):
    global tab
    btn = await tab.find(id=id)
    await btn.hover()

async def query_element(css, timeout=10):
    """CSS 셀렉터로 요소를 찾는다. 없으면 None 반환."""
    global tab
    try:
        return await tab.query(css, timeout=timeout, raise_exc=False)
    except Exception as e:
        print(f"요소 조회 실패({css}): {e}")
        return None

async def type_into(css, text, timeout=10):
    """CSS 셀렉터로 찾은 입력창에 값을 입력한다."""
    el = await query_element(css, timeout=timeout)
    if el is None:
        raise Exception(f"입력창을 찾을 수 없습니다: {css}")
    await el.click()
    await el.type_text(text)
    return el

async def fill_jumin_if_present():
    """주민등록번호 입력창이 화면에 표시되어 있으면 앞 6자리 + 뒤 1자리를 입력한다.

    개편된 홈택스 아이디 로그인은 본인확인을 위해 주민등록번호
    앞 6자리(생년월일)와 뒤 1자리(성별 구분)를 요구한다.
    입력창은 조건부로 노출되므로 존재/표시 여부를 확인 후 처리한다.
    반환: 입력을 수행하면 True, 창이 없으면 False.
    """
    front_el = await query_element(SEL_JUMIN_FRONT, timeout=2)
    if front_el is None:
        return False
    try:
        if not await front_el.is_visible():
            return False
    except Exception:
        return False

    front = JUMIN_FRONT or input('주민등록번호 앞 6자리를 입력하세요: ').strip()
    back = JUMIN_BACK or input('주민등록번호 뒤 1자리를 입력하세요: ').strip()

    await front_el.click()
    await front_el.type_text(front)
    back_el = await query_element(SEL_JUMIN_BACK, timeout=5)
    if back_el is not None:
        await back_el.click()
        await back_el.type_text(back)
    print("주민등록번호 입력 완료")
    return True

async def is_logged_in():
    """로그아웃 요소(또는 텍스트)가 있으면 로그인된 것으로 간주."""
    global tab
    try:
        logout_btn = await tab.find(tag_name='a', title='로그아웃', timeout=2)
        if logout_btn:
            return True
    except Exception:
        pass
    try:
        result = await tab.execute_script(
            "document.body && document.body.innerText.indexOf('로그아웃') > -1")
        return bool(result)
    except Exception:
        return False

async def TryToParse(TESTorREAL):
    global INQ_CONDITION
    global TO_BE_CHANGED
    global tab

    print("TryToParse()")
    try:
        url = "https://www.hometax.go.kr/"
        async with Chrome() as browser:
            tab = await browser.start()
            
            await tab.go_to(url)
            title = await tab.execute_script("document.title")
            print(title)

            # 먼저 로그인 상태 확인
            already_logged_in = await is_logged_in()
            if already_logged_in:
                print("이미 로그인된 상태입니다.")

            if not already_logged_in:
                # 1) 상단 '로그인' 클릭 → 로그인 페이지로 이동
                try:
                    login_btn = await tab.find(tag_name='a', title='로그인', timeout=5)
                    await login_btn.click()
                    print("로그인 페이지로 이동")
                except Exception:
                    # fallback: 텍스트가 '로그인'인 링크 찾기
                    try:
                        login_links = await tab.find_all(tag_name='a', timeout=3)
                        for link in login_links:
                            link_text = await link.text
                            if link_text and link_text.strip() == '로그인':
                                await link.click()
                                print("로그인 페이지로 이동 (텍스트)")
                                break
                    except Exception as e:
                        print(f"로그인 버튼을 찾을 수 없습니다: {e}")
                await asyncio.sleep(2)

                # 2) '아이디 로그인' 탭 선택 (data-tab="login_tab3")
                try:
                    id_tab = await query_element(SEL_ID_LOGIN_TAB, timeout=10)
                    if id_tab is not None:
                        await id_tab.click()
                        print("아이디 로그인 탭 선택 완료")
                        await asyncio.sleep(1.5)
                    else:
                        print("아이디 로그인 탭을 찾을 수 없습니다.")
                except Exception as e:
                    print(f"아이디 로그인 탭 선택 실패: {e}")

                # 3) 아이디 / 비밀번호 입력 후 (필요 시) 주민등록번호 입력 → 로그인 실행
                try:
                    await type_into(SEL_INPUT_ID, LOGIN_ID)
                    print("아이디 입력 완료")

                    await type_into(SEL_INPUT_PW, LOGIN_PW)
                    print("비밀번호 입력 완료")

                    # 폼에 주민등록번호 입력창이 이미 표시된 경우 먼저 입력
                    await fill_jumin_if_present()

                    # 로그인 실행
                    login_submit = await query_element(SEL_LOGIN_SUBMIT, timeout=10)
                    if login_submit is not None:
                        await login_submit.click()
                        print("로그인 실행")
                        await asyncio.sleep(2)
                    else:
                        print("로그인 실행 버튼을 찾을 수 없습니다.")

                    # 로그인 클릭 후 주민등록번호 확인창이 뜨는 경우 입력 후 재실행
                    if await fill_jumin_if_present():
                        login_submit = await query_element(SEL_LOGIN_SUBMIT, timeout=10)
                        if login_submit is not None:
                            await login_submit.click()
                            print("주민등록번호 입력 후 로그인 재실행")
                            await asyncio.sleep(2)
                except Exception as e:
                    print(f"로그인 과정 중 오류: {e}")

            # 로그인 완료 확인 (로그아웃 상태가 될 때까지 대기)
            while True:
                if await is_logged_in():
                    print("로그인됨.")
                    break
                print("홈택스 로그인 해주세요.")
                await asyncio.sleep(3)
            
            await tab.go_to("https://hometax.go.kr/websquare/websquare.wq?w2xPath=/ui/pp/index_pp.xml&tmIdx=1&tm2lIdx=0105040000&tm3lIdx=0105040400")

            await asyncio.sleep(0.5)
            # Switch to iframe - pydoll handles frames differently
            iframe = await tab.find(xpath='//iframe[@id="txppIframe"]')
            tab = await tab.get_frame(iframe)

            await asyncio.sleep(1.5)
            await clickIFclickable('rdoSearch_input_2', 0.3) #분기별 옵션 선택

            select_year = await tab.find(id='selectYear')
            select_qrt = await tab.find(id='selectQrt')

            year_options = await select_year.find_all(tag_name="option")
            qrt_options = await select_qrt.find_all(tag_name="option")
            menu_list = await MakeMenuList(year_options, qrt_options)
            while(True):
                answer = show_menu('무엇을 도와드릴까요?', menu_list)

                if('항목 조회:' in answer):
                    await clickIFclickable('rdoSearch_input_2', 0.3) #분기별 옵션 선택

                    splited_answer= answer.split(':')
                    selected_year= splited_answer[1].strip()
                    selected_qrt= splited_answer[2].strip()

                    # Select year option
                    year_options = await select_year.find_all(tag_name="option")
                    for option in year_options:
                        option_text = await option.text
                        if option_text == selected_year:
                            await option.click()
                            break
                    
                    # Select quarter option
                    qrt_options = await select_qrt.find_all(tag_name="option")
                    for option in qrt_options:
                        option_text = await option.text
                        if option_text == selected_qrt:
                            await option.click()
                            break

                    # Select condition
                    selectbox4 = await tab.find(id='selectbox4')
                    selectbox4_options = await selectbox4.find_all(tag_name="option")
                    for option in selectbox4_options:
                        option_text = await option.text
                        if option_text == INQ_CONDITION:
                            await option.click()
                            break
                    
                    await clickIFclickable('btnSearch', 0.1)
                    await asyncio.sleep(1)
                    continue

                elif('조회대상 수정' in answer):
                    if(INQ_CONDITION == "불공제대상"):
                        INQ_CONDITION = "공제대상"
                    elif(INQ_CONDITION == "공제대상"):
                        INQ_CONDITION = "불공제대상"
                    menu_list = await MakeMenuList(year_options, qrt_options)
                    continue
                elif('변경대상 수정' in answer):
                    if(TO_BE_CHANGED == "불공제"):
                        TO_BE_CHANGED = "공제"
                    elif(TO_BE_CHANGED == "공제"):
                        TO_BE_CHANGED = "불공제"
                    menu_list = await MakeMenuList(year_options, qrt_options)
                    continue
                elif('변경하기.' in answer):
                    while True:
                        textof_DOM_total_elem = await tab.find(id='txtTotal')
                        textof_DOM_totalpage_elem = await tab.find(id='txtTotalPage')
                        textof_DOM_total = await textof_DOM_total_elem.text
                        textof_DOM_totalpage = await textof_DOM_totalpage_elem.text
                        total = int(textof_DOM_total)
                        totalpage = int(textof_DOM_totalpage)
                        print("총 페이지: " + str(totalpage))
                        print("총 항목개수: " + str(total))

                        if(total == 0): # 항목이 없으면 종료.
                            print("더 이상 항목이 없으므로 종료!")
                            break

                        countof_disabled = await AllClickOnThisPage()
                        print("이 페이지에서 선택불가항목: " + str(countof_disabled))
                        if(countof_disabled == total): # 더 이상 선택할 항목이 없고
                            print("선택불가항목 "+str(countof_disabled)+"만 남음!")
                            break
                            
                        elif(countof_disabled == 10):
                            try:
                                next_btn = await tab.find(id='pglNavi_next_btn')
                                is_visible = await next_btn.is_visible()
                                print("다음 페이지 버튼이 있는지? " + str(is_visible))
                                if is_visible:
                                    print("다음 페이지로 넘어갑니다!")
                                    await clickIFclickable('pglNavi_next_btn', 0.5)
                                else: # 다음 페이지 버튼도 없고 선택불가항목만 남아있으면 종료.
                                    print("더 이상 선택할 항목이 없습니다!")
                                    break
                            except Exception as e:
                                print(f"다음 페이지 버튼 찾기 실패: {e}")
                                break
                    continue
                else:
                    exit(0)
        
    except Exception as e:
        print(e)

print("test1")
asyncio.run(TryToParse(True))
