# -*- coding: utf-8 -*-
#
# 국세청 홈택스 부가가치세 매입세액 공제/불공제 일괄 변경 자동화 (Playwright 버전)
#
# 2026 홈택스 개편(아이디 로그인 + 주민등록번호 본인확인) 대응.
# 기존 pydoll 버전(../hometax.go.kr/)을 Playwright(sync API)로 새로 작성한 것.
#
#   pip install -r requirements.txt
#   python3 hometax_playwright.py
#
# 시스템에 설치된 Google Chrome 을 사용합니다(channel="chrome").

import sys
import time

from playwright.sync_api import sync_playwright


# ============================ 설정 ============================
INQ_CONDITION = "불공제대상"  # 조회 대상: 공제대상 또는 불공제대상
TO_BE_CHANGED = "공제"        # 변경 대상: 공제 또는 불공제

# --- 로그인 정보 ---
LOGIN_ID = "tangibleidea"
LOGIN_PW = "f3bab@6845"
# 주민등록번호는 개인정보이므로 아래를 비워두면('') 로그인 시 콘솔에서 입력받습니다.
JUMIN_FRONT = "900206"  # 주민등록번호 앞 6자리 (생년월일)
JUMIN_BACK = "1"        # 주민등록번호 뒤 1자리 (성별 구분 숫자)

BASE_URL = "https://www.hometax.go.kr/"
DEDUCTION_URL = (
    "https://hometax.go.kr/websquare/websquare.wq?w2xPath=/ui/pp/index_pp.xml"
    "&tmIdx=1&tm2lIdx=0105040000&tm3lIdx=0105040400"
)

# --- 아이디 로그인 화면 셀렉터 (라이브 페이지 검사로 확인, 2026 개편 기준) ---
SEL_ID_LOGIN_TAB = '[data-tab="login_tab3"]'          # '아이디 로그인' 탭
SEL_INPUT_ID = 'input[name="iptUserId"]'              # 아이디 입력
SEL_INPUT_PW = 'input[name="iptUserPw"]'              # 비밀번호 입력
# 로그인 클릭 후 뜨는 '아이디 로그인 2차 인증' 모달의 주민등록번호 입력창.
# 로그인 폼에도 같은 name 의 숨겨진 입력창이 있으므로 :visible 로 '보이는' 것만 선택한다.
SEL_JUMIN_FRONT = 'input[name="iptUserJuminNo1"]:visible'  # 주민번호 앞 6자리
SEL_JUMIN_BACK = 'input[name="iptUserJuminNo2"]:visible'   # 주민번호 뒤 1자리
SEL_LOGIN_SUBMIT = 'a.logingbtn[title="로그인"]'            # 로그인 실행 버튼 (간편인증 버튼과 구분)
SEL_2FA_CONFIRM = 'input[value="확인"]:visible'            # 2차 인증 모달의 '확인' 버튼


# ============================ 공통 유틸 ============================
def show_menu(message, choices):
    """간단한 콘솔 메뉴."""
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
            print("잘못된 선택입니다. 다시 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")


def make_menu_list(year_texts, qrt_texts):
    menu_list = []
    for y in year_texts:
        for q in qrt_texts:
            menu_list.append(f"{INQ_CONDITION} 항목 조회: {y}:{q}")
    menu_list.append(f"전체 아이템을 {TO_BE_CHANGED} 항목으로 변경하기.")
    menu_list.append(f"조회대상 수정 (현재:{INQ_CONDITION})")
    menu_list.append(f"변경대상 수정 (현재:{TO_BE_CHANGED})")
    menu_list.append("종료.")
    return menu_list


def click_if_clickable(ctx, elem_id, waittime=3):
    """id 로 요소를 찾아 클릭. ctx 는 Page 또는 Frame."""
    loc = ctx.locator(f"#{elem_id}")
    try:
        loc.wait_for(state="visible", timeout=10000)
        try:
            print(f"{loc.inner_text().strip()} is clickable.")
        except Exception:
            pass
        time.sleep(waittime)
        loc.click()
        time.sleep(waittime)
    except Exception as e:
        print(e)
        print("try another way")
        try:
            ctx.locator(f"#{elem_id}").click(timeout=5000)
            time.sleep(waittime)
        except Exception as e2:
            print(f"Second attempt failed: {e2}")


# ============================ 로그인 ============================
def is_logged_in(page):
    """화면에 '로그아웃' 버튼/링크가 보이면 로그인된 것으로 간주.

    메인/로그인 페이지 안내문에도 '로그아웃'이라는 '텍스트'가 포함되어 있으므로,
    단순 텍스트 검색이 아니라 클릭 가능한(a/button) 요소가 '보이는지'로 판별한다.
    """
    try:
        return page.evaluate(
            """() => {
                const btns = Array.from(document.querySelectorAll('a,button'));
                return btns.some(e => e.offsetParent !== null &&
                    (e.getAttribute('title') === '로그아웃' ||
                     (e.textContent || '').trim() === '로그아웃'));
            }"""
        )
    except Exception:
        return False


def fill_jumin_if_present(page):
    """'아이디 로그인 2차 인증' 주민등록번호 입력창이 뜨면 앞 6자리 + 뒤 1자리 입력.

    로그인 클릭 후 개인정보 보호용 2차 인증 모달이 뜨며, 가입자(대표자)
    주민번호 앞 7자리(= 앞 6자리 + 뒤 1자리)를 요구한다.
    입력창은 조건부로 노출되므로 '보이는' 입력창(:visible)만 대상으로 한다.
    반환: 입력을 수행하면 True, 창이 없으면 False.
    """
    front = page.locator(SEL_JUMIN_FRONT)
    try:
        if front.count() == 0:
            return False
    except Exception:
        return False

    f = JUMIN_FRONT or input("주민등록번호 앞 6자리를 입력하세요: ").strip()
    b = JUMIN_BACK or input("주민등록번호 뒤 1자리를 입력하세요: ").strip()

    front.first.fill(f)
    back = page.locator(SEL_JUMIN_BACK)
    if back.count() > 0:
        back.first.fill(b)
    print("주민등록번호(2차 인증) 입력 완료")
    return True


def login(page):
    if is_logged_in(page):
        print("이미 로그인된 상태입니다.")
        return

    # 1) 상단 '로그인' 클릭 → 로그인 페이지로 이동
    try:
        page.locator('a[title="로그인"]').first.click()
        print("로그인 페이지로 이동")
    except Exception:
        try:
            page.get_by_text("로그인", exact=True).first.click()
            print("로그인 페이지로 이동 (텍스트)")
        except Exception as e:
            print(f"로그인 버튼을 찾을 수 없습니다: {e}")
    page.wait_for_timeout(2000)

    # 2) '아이디 로그인' 탭 선택 (data-tab="login_tab3")
    try:
        page.locator(SEL_ID_LOGIN_TAB).click(timeout=10000)
        print("아이디 로그인 탭 선택 완료")
        page.wait_for_timeout(1500)
    except Exception as e:
        print(f"아이디 로그인 탭 선택 실패: {e}")

    # 3) 아이디 / 비밀번호 (+ 필요 시 주민번호) 입력 후 로그인 실행
    try:
        page.locator(SEL_INPUT_ID).fill(LOGIN_ID)
        print("아이디 입력 완료")
        page.locator(SEL_INPUT_PW).fill(LOGIN_PW)
        print("비밀번호 입력 완료")

        page.locator(SEL_LOGIN_SUBMIT).click(timeout=10000)
        print("로그인 실행")

        # 로그인 클릭 → '아이디 로그인 2차 인증' 모달이 뜨면 주민번호 입력 후 '확인'
        for _ in range(10):  # 모달이 뜰 때까지 최대 ~5초 대기
            if fill_jumin_if_present(page):
                try:
                    page.locator(SEL_2FA_CONFIRM).first.click(timeout=5000)
                    print("2차 인증(주민등록번호) 확인")
                except Exception:
                    # 확인 버튼을 못 찾으면 로그인 버튼 재시도
                    page.locator(SEL_LOGIN_SUBMIT).click(timeout=5000)
                page.wait_for_timeout(2000)
                break
            page.wait_for_timeout(500)
    except Exception as e:
        print(f"로그인 과정 중 오류: {e}")

    # 4) 로그인 완료 대기
    while not is_logged_in(page):
        print("홈택스 로그인 해주세요.")
        page.wait_for_timeout(3000)
    print("로그인됨.")


# ============================ 항목 변경 ============================
def all_click_on_this_page(frame):
    """현재 페이지의 항목을 전체 선택하고 TO_BE_CHANGED 로 변경 후 적용."""
    frame.locator('//input[@title="전체선택"]').click()

    countof_disabled = 0  # 선택불가항목 카운트
    selects = frame.locator('//div[@class="w2selectbox_native_innerDiv"]//select')
    n = selects.count()
    for i in range(n):
        sel = selects.nth(i)
        try:
            disabled = sel.is_disabled()
        except Exception:
            disabled = sel.get_attribute("disabled") is not None
        if disabled:
            print("변경할 수 없는 선택항목 (면세 또는 공제 불가항목)")
            countof_disabled += 1
        else:
            try:
                sel.select_option(label=TO_BE_CHANGED)
            except Exception as e:
                print(f"항목 변경 실패: {e}")

    click_if_clickable(frame, "trigger19", 0.3)
    # alert 는 page.on("dialog") 핸들러가 자동 수락하므로 잠시 대기만.
    time.sleep(1)
    return countof_disabled


def run_menu(page, frame):
    global INQ_CONDITION, TO_BE_CHANGED

    click_if_clickable(frame, "rdoSearch_input_2", 0.3)  # 분기별 옵션 선택

    year_texts = [t.strip() for t in frame.locator("#selectYear option").all_inner_texts()]
    qrt_texts = [t.strip() for t in frame.locator("#selectQrt option").all_inner_texts()]
    menu_list = make_menu_list(year_texts, qrt_texts)

    while True:
        answer = show_menu("무엇을 도와드릴까요?", menu_list)

        if "항목 조회:" in answer:
            click_if_clickable(frame, "rdoSearch_input_2", 0.3)  # 분기별 옵션 선택

            splited = answer.split(":")
            selected_year = splited[1].strip()
            selected_qrt = splited[2].strip()

            frame.locator("#selectYear").select_option(label=selected_year)
            frame.locator("#selectQrt").select_option(label=selected_qrt)
            frame.locator("#selectbox4").select_option(label=INQ_CONDITION)

            click_if_clickable(frame, "btnSearch", 0.1)
            time.sleep(1)
            continue

        elif "조회대상 수정" in answer:
            INQ_CONDITION = "공제대상" if INQ_CONDITION == "불공제대상" else "불공제대상"
            menu_list = make_menu_list(year_texts, qrt_texts)
            continue

        elif "변경대상 수정" in answer:
            TO_BE_CHANGED = "공제" if TO_BE_CHANGED == "불공제" else "불공제"
            menu_list = make_menu_list(year_texts, qrt_texts)
            continue

        elif "변경하기." in answer:
            while True:
                total = int(frame.locator("#txtTotal").inner_text())
                totalpage = int(frame.locator("#txtTotalPage").inner_text())
                print("총 페이지: " + str(totalpage))
                print("총 항목개수: " + str(total))

                if total == 0:  # 항목이 없으면 종료.
                    print("더 이상 항목이 없으므로 종료!")
                    break

                countof_disabled = all_click_on_this_page(frame)
                print("이 페이지에서 선택불가항목: " + str(countof_disabled))

                if countof_disabled == total:  # 선택 가능한 항목이 없음
                    print("선택불가항목 " + str(countof_disabled) + "만 남음!")
                    break
                elif countof_disabled == 10:
                    nxt = frame.locator("#pglNavi_next_btn")
                    try:
                        visible = nxt.is_visible()
                    except Exception:
                        visible = False
                    print("다음 페이지 버튼이 있는지? " + str(visible))
                    if visible:
                        print("다음 페이지로 넘어갑니다!")
                        click_if_clickable(frame, "pglNavi_next_btn", 0.5)
                    else:
                        print("더 이상 선택할 항목이 없습니다!")
                        break
            continue

        else:
            break


# ============================ 메인 ============================
def main():
    print("TryToParse()")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",  # 시스템에 설치된 Google Chrome 사용
            args=["--disable-popup-blocking", "--start-maximized"],
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        # 홈택스의 alert/confirm 자동 수락
        page.on("dialog", lambda dialog: dialog.accept())

        try:
            page.goto(BASE_URL)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)
            print(page.title())

            login(page)

            page.goto(DEDUCTION_URL)
            page.wait_for_timeout(1500)

            iframe_el = page.wait_for_selector("#txppIframe", timeout=30000)
            frame = iframe_el.content_frame()
            page.wait_for_timeout(1500)

            run_menu(page, frame)
        except Exception as e:
            print(e)
        finally:
            input("종료하려면 Enter 를 누르세요...")
            browser.close()


if __name__ == "__main__":
    main()
