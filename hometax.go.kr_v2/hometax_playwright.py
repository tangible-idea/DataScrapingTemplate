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

import getpass
import os
import sys
import time

from playwright.sync_api import sync_playwright


# ============================ 설정 ============================
INQ_CONDITION = "불공제대상"  # 조회 대상: 공제대상 또는 불공제대상
TO_BE_CHANGED = "공제"        # 변경 대상: 공제 또는 불공제

# '일괄 변경' 메뉴가 처리할 (연도, 분기) 목록.
# 화면의 선택박스 옵션 텍스트와 정확히 일치해야 한다. (예: '2026년', '1분기')
BATCH_TARGETS = [
    ("2026년", "1분기"),
    ("2026년", "2분기"),
]


def load_dotenv(path):
    """의존성 없이 .env 를 읽어 os.environ 에 채운다.

    이미 환경변수로 설정된 값은 덮어쓰지 않는다(셸 export 가 우선).
    KEY=VALUE 형식만 지원하며 '#' 로 시작하는 줄과 빈 줄은 무시한다.
    """
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


# 스크립트와 같은 폴더의 .env 를 읽는다. (.env 는 git 에 올리지 않는다)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# --- 로그인 정보 (환경변수 또는 .env) ---
# 아이디/비밀번호/주민등록번호는 코드에 두지 않는다.
# 비어 있으면 실행 중 콘솔에서 입력받는다.
LOGIN_ID = os.environ.get("HOMETAX_ID", "")
LOGIN_PW = os.environ.get("HOMETAX_PW", "")
JUMIN_FRONT = os.environ.get("HOMETAX_JUMIN_FRONT", "")  # 주민등록번호 앞 6자리
JUMIN_BACK = os.environ.get("HOMETAX_JUMIN_BACK", "")    # 주민등록번호 뒤 1자리

BASE_URL = "https://www.hometax.go.kr/"
# 메뉴 경로를 클릭했을 때 실제로 도달하는 URL (라이브 확인, 2026 개편 기준).
# tmIdx=46(계산서·영수증·카드) / tm2lIdx=4608020000(사업용 신용카드 사용내역)
#                              / tm3lIdx=4608020100(매입세액 공제 확인/변경)
# 개편 전 URL(websquare.wq + tmIdx=1&tm2lIdx=0105040000&tm3lIdx=0105040400)은 더 이상 동작하지 않는다.
DEDUCTION_URL = (
    "https://hometax.go.kr/websquare/websquare.html?w2xPath=/ui/pp/index_pp.xml"
    "&tmIdx=46&tm2lIdx=4608020000&tm3lIdx=4608020100"
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

# 도착 화면 이름. 제대로 들어왔는지 확인용.
SCREEN_NAME = "사업용신용카드 매입세액 공제 확인/변경"

# --- 메뉴 네비게이션 셀렉터 ---
# 경로: 계산서·영수증·카드 > 신용카드 매입 > 사업용 신용카드 사용내역 > 매입세액 공제 확인/변경
#
# 기본은 DEDUCTION_URL 직접 이동이다. 메뉴를 클릭해서 들어가면 WebSquare 가
# URL 만 바꾸고 화면 로더를 제대로 태우지 않아 본문 iframe 이 about:blank 로
# 남는 경우가 있어서, 전체 페이지 로드로 들어가는 쪽이 안정적이다.
# 아래 메뉴 클릭 경로는 URL 이 다시 바뀌었을 때를 대비해 남겨둔다
# (USE_MENU_NAVIGATION = True 로 켤 수 있다).
#
# 상단 GNB 는 '전체메뉴' 오버레이 안에만 있다. 오버레이 좌측 레일에서 대분류를 고르면
# 우측에 중분류 섹션들이 펼쳐지고, 소분류는 '+' 를 눌러야 나타난다.
# 좌측 레일 링크의 id 는 WebSquare 가 만든 uuid(mf_wfHeader_wq_uuid_369 등)라 빌드마다
# 바뀔 수 있으므로 텍스트로 찾고, 메뉴 항목은 안정적인 메뉴코드 id 를 쓴다.
USE_MENU_NAVIGATION = False
SEL_ALL_MENU = 'a.btn_all[title="전체메뉴"]'                  # '전체메뉴' 열기
MENU_CATEGORY = "계산서·영수증·카드"                          # 대분류 (tmIdx=46)
SEL_MENU_CATEGORY = f'//a[./span[normalize-space(text())="{MENU_CATEGORY}"]]'
SEL_MENU_SECTION = "#menuUl46_4608000000"                    # 중분류 '신용카드 매입'
SEL_MENU_CARD_USAGE = "#menuAtag_4608020000"                 # '사업용 신용카드 사용내역' (펼치기)
SEL_MENU_DEDUCTION = "#menuAtag_4608020100"                  # '매입세액 공제 확인/변경'
# 주의: '매입세액 공제 확인/변경'은 '화물운전자 복지카드' 아래(menuAtag_4608030100)에도
# 같은 이름으로 존재한다. 반드시 메뉴코드로 구분해야 한다.

# WebSquare 안내 팝업(네이티브 alert 아님. 예: "로그인 정보가 없습니다.")의 확인 버튼.
# id 에 난수가 섞여 있어(mf_wfHeader_info3989364875_wframe_btn_confirm) class 로 잡는다.
# 업무 화면의 일반 '확인' 버튼까지 누르지 않도록 반드시 팝업(w2window) 안으로 범위를 좁힌다.
SEL_WS_POPUP_CONFIRM = '[class*="w2window"] input.w2trigger[value="확인"]:visible'

# --- 업무 화면 요소 id ---
# 2026 개편 후 업무 화면은 iframe(txppIframe)이 아니라 **메인 문서**에 직접 그려지고,
# 모든 요소 id 에 'mf_txppWframe_' 접두사가 붙는다.
#   개편 전: #selectYear        개편 후: #mf_txppWframe_selectYear
# txppIframe 은 src="about:blank" 인 빈 껍데기로 남아 있으므로 거기서 찾으면 안 된다.
WORK_ID_PREFIX = "mf_txppWframe_"


def wsel(*names):
    """업무 화면 요소의 id 셀렉터를 만든다.

    접두사가 붙은 개편 후 id 와 접두사 없는 개편 전 id 를 모두 매칭하므로,
    사이트가 어느 쪽이든 동작한다. 이름을 여러 개 주면 모두 후보에 넣는다
    (예: pglNavi 는 개편으로 이름 자체가 next_btn → nextPage_btn 으로 바뀜).
    여러 개가 매칭될 수 있으니 쓸 때는 .first 를 붙인다.
    """
    parts = []
    for n in names:
        parts.append(f"#{WORK_ID_PREFIX}{n}")
        parts.append(f"#{n}")
    return ", ".join(parts)


SEL_SELECT_YEAR = wsel("selectYear")
SEL_SELECT_QRT = wsel("selectQrt")
SEL_SELECT_COND = wsel("selectbox4")      # 조회 대상(-all-/공제대상/불공제대상)
SEL_TXT_TOTAL = wsel("txtTotal")
SEL_TXT_TOTALPAGE = wsel("txtTotalPage")
SEL_APPLY_BTN = wsel("trigger19")         # 변경 내용 적용
SEL_NEXT_PAGE = wsel("pglNavi_nextPage_btn", "pglNavi_next_btn")

# 목록 헤더의 전체선택 체크박스. 이걸 누르면 현재 페이지 항목이 전부 선택된다.
# WebSquare 는 실제 input 을 감추고 label 만 보여주므로 label 을 눌러야 한다.
#   <label class="w2checkbox_label" for="wq_uuid_..._chk_checkboxLabel__id">전체선택</label>
# for 속성값은 uuid(wq_uuid_2012_...)라 빌드마다 바뀌므로 쓰지 않는다.
# 라벨 텍스트로 잡으면 DOM 순서에 의존하지 않아 가장 안전하고,
# 못 찾으면 맨 위(.first) 체크박스로 폴백한다.
SEL_HEADER_CHECKBOX = [
    'label.w2checkbox_label:text-is("전체선택")',
    '.w2checkbox_label',
]

# '공제여부 결정' 열의 선택박스가 가지는 옵션.
# 연도/분기/조회대상 선택박스와 구분하는 기준으로 쓴다.
DEDUCTION_OPTIONS = {"공제", "불공제"}

# 업무 화면이 어느 컨텍스트에 그려졌는지 판별하는 마커.
# 이 중 하나라도 있으면 그 컨텍스트가 업무 화면이다.
SEL_WORK_MARKERS = [SEL_SELECT_YEAR, wsel("btnSearch"), wsel("rdoSearch_input_2")]

# --- 조회 조건 ---
# id 우선, 실패 시 라벨/텍스트로 폴백한다.
SEL_QUARTERLY = [wsel("rdoSearch_input_2"), 'label:text-is("분기별")']
SEL_SEARCH_BTN = [wsel("btnSearch"), 'input[value="조회"]']


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
    targets = " + ".join(f"{y} {q}" for y, q in BATCH_TARGETS)
    menu_list.append(f"[{targets}] 조회부터 변경까지 일괄 변경 ({INQ_CONDITION}→{TO_BE_CHANGED})")
    for y in year_texts:
        for q in qrt_texts:
            menu_list.append(f"{INQ_CONDITION} 항목 조회: {y}:{q}")
    menu_list.append(f"전체 아이템을 {TO_BE_CHANGED} 항목으로 변경하기.")
    menu_list.append(f"조회대상 수정 (현재:{INQ_CONDITION})")
    menu_list.append(f"변경대상 수정 (현재:{TO_BE_CHANGED})")
    menu_list.append("종료.")
    return menu_list


def click_selector(ctx, selector, what, waittime=0.3):
    """셀렉터로 요소를 찾아 클릭. ctx 는 Page 또는 Frame.

    보이지 않는다는 이유로 실패하면 dispatch_event 로 한 번 더 시도한다.
    """
    loc = ctx.locator(selector).first
    try:
        loc.wait_for(state="visible", timeout=10000)
        time.sleep(waittime)
        loc.click()
        time.sleep(waittime)
        print(f"{what} 클릭")
        return True
    except Exception as e:
        print(f"{what} 클릭 실패: {e}")
        try:
            loc.dispatch_event("click")
            time.sleep(waittime)
            print(f"{what} 클릭 (dispatch_event)")
            return True
        except Exception as e2:
            print(f"{what} 재시도도 실패: {e2}")
            return False


def click_first_available(ctx, selectors, what, timeout=5000):
    """셀렉터 후보를 순서대로 시도해 처음 클릭되는 것을 클릭.

    홈택스 개편으로 id 가 바뀌어도 라벨/텍스트 폴백으로 살아남게 하기 위한 헬퍼.
    ctx 는 Page 또는 Frame. 하나도 못 누르면 False 반환.
    """
    for sel in selectors:
        try:
            loc = ctx.locator(sel).first
            loc.wait_for(state="visible", timeout=timeout)
            loc.click(timeout=timeout)
            print(f"{what} 클릭 ({sel})")
            return True
        except Exception:
            continue
    print(f"{what} 를 찾지 못했습니다. 시도한 셀렉터: {selectors}")
    return False


def click_menu_anchor(ctx, selector, what, timeout=10000, required=True):
    """전체메뉴 오버레이의 메뉴 링크를 클릭한다.

    메뉴 링크는 전부 href="javascript:void(0);" + 클릭 핸들러 구조라,
    오버레이 애니메이션/반응형 레이아웃 탓에 요소가 '보이지 않는' 것으로
    판정되어도 dispatch_event 로 핸들러를 직접 태우면 정상 동작한다.
    실제로 전체메뉴 오버레이 항목은 대부분 이 경로로 눌린다. 일반 클릭에
    긴 타임아웃을 주면 매번 그만큼 낭비되므로 짧게 시도하고 바로 폴백한다.
    required=False 이면 실패해도 예외 없이 False 만 돌려준다.
    """
    loc = ctx.locator(selector).first
    try:
        loc.wait_for(state="attached", timeout=timeout)
    except Exception:
        if required:
            raise
        print(f"{what} 없음 (건너뜀)")
        return False

    try:
        loc.scroll_into_view_if_needed(timeout=2000)
    except Exception:
        pass

    try:
        loc.click(timeout=2000)
        print(f"{what} 클릭")
        return True
    except Exception:
        try:
            loc.dispatch_event("click")
            print(f"{what} 클릭 (dispatch_event)")
            return True
        except Exception as e:
            if required:
                raise
            print(f"{what} 클릭 실패 (건너뜀): {e}")
            return False


def dismiss_ws_popup(page):
    """WebSquare 안내 팝업이 떠 있으면 '확인'을 눌러 닫는다.

    홈택스는 네이티브 alert 대신 자체 모달(w2window)을 쓰는 곳이 많아
    page.on("dialog") 핸들러로는 잡히지 않는다. 세션 만료/미로그인 시
    "로그인 정보가 없습니다." 팝업이 이 형태로 뜬다.
    반환: 닫았으면 True.
    """
    try:
        btn = page.locator(SEL_WS_POPUP_CONFIRM)
        if btn.count() == 0:
            return False
        try:
            # w2window_content 전체를 읽으면 '레이어팝업시작' 같은 스크린리더용
            # 텍스트가 섞이므로 본문 영역(.pop_cbox)만 읽는다.
            msg = page.locator("div.pop_cbox").first.inner_text().strip()
            if msg:
                print(f"안내 팝업: {msg}")
        except Exception:
            pass
        btn.first.click(timeout=5000)
        page.wait_for_timeout(500)
        return True
    except Exception:
        return False


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


def require_credentials():
    """아이디/비밀번호를 확보한다. 환경변수에 없으면 콘솔에서 입력받는다."""
    global LOGIN_ID, LOGIN_PW
    if not LOGIN_ID:
        LOGIN_ID = input("홈택스 아이디: ").strip()
    if not LOGIN_PW:
        # getpass 는 입력이 화면에 찍히지 않는다.
        LOGIN_PW = getpass.getpass("홈택스 비밀번호: ")
    if not LOGIN_ID or not LOGIN_PW:
        raise RuntimeError("아이디/비밀번호가 필요합니다. .env 를 설정하세요.")


def login(page):
    if is_logged_in(page):
        print("이미 로그인된 상태입니다.")
        return

    require_credentials()

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


# ============================ 메뉴 이동 ============================
def goto_deduction_page(page):
    """'사업용신용카드 매입세액 공제 확인/변경' 화면으로 이동한다.

    기본은 DEDUCTION_URL 로 전체 페이지 로드. 메뉴를 클릭해서 들어가면
    WebSquare 가 URL 만 바꾸고 본문 iframe 을 about:blank 로 남기는 일이 있어
    직접 이동이 더 안정적이다.
    USE_MENU_NAVIGATION = True 면 실제 메뉴 클릭 경로를 밟는다.
    """
    print(f"\n[화면 이동] {SCREEN_NAME}")

    if not USE_MENU_NAVIGATION:
        page.goto(DEDUCTION_URL)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2500)
        print(f"이동 완료: {page.title()}")
        if dismiss_ws_popup(page):
            raise RuntimeError("로그인 세션이 없습니다. 로그인 후 다시 시도하세요.")
        return

    print("[메뉴 경로] 계산서·영수증·카드 > 신용카드 매입 "
          "> 사업용 신용카드 사용내역 > 매입세액 공제 확인/변경")
    try:
        # 1) '전체메뉴' 열기 — 상단 GNB 는 이 오버레이 안에만 있다.
        page.locator(SEL_ALL_MENU).click(timeout=15000)
        print("전체메뉴 열기")
        page.wait_for_timeout(1200)

        # 2) 좌측 레일에서 대분류 '계산서·영수증·카드' 선택.
        #    오버레이를 열면 이 대분류가 기본 선택되어 있으므로 실패해도 진행한다.
        click_menu_anchor(page, SEL_MENU_CATEGORY, MENU_CATEGORY, required=False)
        page.wait_for_timeout(800)

        # 3) 중분류 '신용카드 매입' 섹션 확인 (기본으로 펼쳐져 있다)
        page.locator(SEL_MENU_SECTION).first.wait_for(state="attached", timeout=10000)
        print("신용카드 매입 섹션 확인")

        # 4) '사업용 신용카드 사용내역' 의 '+' 를 눌러 하위 메뉴를 펼친다.
        click_menu_anchor(page, SEL_MENU_CARD_USAGE, "사업용 신용카드 사용내역 펼치기")
        page.wait_for_timeout(1000)

        # 5) '매입세액 공제 확인/변경' 클릭 → 업무 화면으로 이동
        click_menu_anchor(page, SEL_MENU_DEDUCTION, "매입세액 공제 확인/변경")
        page.wait_for_timeout(2500)
    except Exception as e:
        print(f"메뉴 클릭 실패({e}) → 딥링크 URL 로 이동합니다.")
        page.goto(DEDUCTION_URL)
        page.wait_for_timeout(2500)

    # 세션이 끊겼으면 "로그인 정보가 없습니다." 팝업이 뜬다.
    if dismiss_ws_popup(page):
        raise RuntimeError("로그인 세션이 없습니다. 로그인 후 다시 시도하세요.")


def dump_frames(page):
    """진단용: 현재 페이지의 프레임 구성을 출력한다."""
    print("\n--- 프레임 구성 진단 ---")
    print(f"  page.url = {page.url}")
    for f in page.frames:
        try:
            marks = [m for m in SEL_WORK_MARKERS if f.locator(m).count() > 0]
        except Exception:
            marks = []
        print(f"  frame name={f.name!r} url={f.url[:80]!r} 발견된요소={marks}")
    try:
        for el in page.locator("iframe").all():
            print(f"  iframe id={el.get_attribute('id')!r} "
                  f"name={el.get_attribute('name')!r} "
                  f"src={(el.get_attribute('src') or '')[:60]!r} "
                  f"visible={el.is_visible()}")
    except Exception:
        pass
    print("--- 진단 끝 ---\n")


def open_work_context(page, timeout=30000):
    """업무 화면이 실제로 그려진 컨텍스트(Frame 또는 Page)를 찾아 돌려준다.

    개편 전에는 모든 업무 화면이 iframe(txppIframe) 안에 들어갔지만,
    개편 후에는 본문이 **메인 문서**에 직접 그려지고 mf_txppIframe 은
    src="about:blank" 인 빈 껍데기로 남는다.
    그래서 iframe 을 고정해 기다리지 않고, 조회 조건 요소(SEL_WORK_MARKERS)가
    실제로 존재하는 컨텍스트를 프레임 전체에서 찾는다.
    """
    deadline = time.time() + timeout / 1000.0
    while time.time() < deadline:
        # 메인 문서 → 하위 프레임 순으로 마커를 찾는다.
        for ctx in [page] + list(page.frames):
            for marker in SEL_WORK_MARKERS:
                try:
                    if ctx.locator(marker).count() > 0:
                        where = "메인 문서" if ctx is page else f"프레임 {ctx.name or ctx.url[:50]!r}"
                        print(f"업무 화면 발견: {where} (마커 {marker})")
                        return ctx
                except Exception:
                    continue
        # 안내 팝업이 떠 있으면 본문이 안 그려질 수 있으므로 닫아준다.
        dismiss_ws_popup(page)
        page.wait_for_timeout(500)

    dump_frames(page)
    raise RuntimeError(
        "업무 화면을 찾지 못했습니다. 위 '프레임 구성 진단' 출력을 확인하세요. "
        "조회 조건 요소의 id 가 개편으로 바뀌었을 수 있습니다."
    )


def select_quarterly(frame):
    """조회 기간 단위를 '분기별' 로 선택."""
    return click_first_available(frame, SEL_QUARTERLY, "분기별")


def click_search(frame):
    """'조회' 실행."""
    ok = click_first_available(frame, SEL_SEARCH_BTN, "조회")
    if ok:
        # ctx 는 Page 일 수도 Frame 일 수도 있는데 둘 다 wait_for_timeout 을 가진다.
        frame.wait_for_timeout(1500)
    return ok


# ============================ 항목 변경 ============================
def row_deduction_selects(frame):
    """'공제여부 결정' 열의 선택박스만 골라낸다.

    연도/분기/조회대상 선택박스도 화면에 같이 있으므로 위치나 class 로
    잡으면 섞인다. 옵션이 공제/불공제인 것만 행 선택박스로 판단한다.
    """
    picked = []
    selects = frame.locator("select")
    for i in range(selects.count()):
        sel = selects.nth(i)
        try:
            opts = {t.strip() for t in sel.locator("option").all_inner_texts()}
        except Exception:
            continue
        if DEDUCTION_OPTIONS <= opts:
            picked.append(sel)
    return picked


def all_click_on_this_page(frame, page):
    """맨 위 체크박스 클릭 → '공제여부 결정'을 TO_BE_CHANGED 로 변경 → 적용.

    반환: (선택불가 개수, 실제로 값이 바뀐 개수)
    """
    if not click_first_available(frame, SEL_HEADER_CHECKBOX, "전체선택 체크박스"):
        raise RuntimeError(
            f"전체선택 체크박스를 찾지 못했습니다 ({SEL_HEADER_CHECKBOX})."
        )

    selects = row_deduction_selects(frame)
    n = len(selects)
    print(f"'공제여부 결정' 선택박스 {n}개 발견")
    if n == 0:
        raise RuntimeError(
            "'공제여부 결정' 선택박스를 찾지 못했습니다. "
            f"옵션 {DEDUCTION_OPTIONS} 를 가진 select 가 없습니다. "
            "목록이 비었거나 화면 구조가 바뀐 것입니다."
        )

    countof_disabled = 0  # 선택불가항목 카운트
    countof_changed = 0   # 실제로 값이 바뀐 개수
    for i, sel in enumerate(selects):
        try:
            disabled = sel.is_disabled()
        except Exception:
            disabled = sel.get_attribute("disabled") is not None
        if disabled:
            countof_disabled += 1
            continue
        try:
            before = sel.input_value()
            sel.select_option(label=TO_BE_CHANGED)
            after = sel.input_value()
            if before != after:
                countof_changed += 1
        except Exception as e:
            print(f"  {i}번 항목 변경 실패: {e}")

    print(f"선택불가 {countof_disabled}건 / 값 변경 {countof_changed}건")
    if countof_changed == 0:
        print("  주의: 값이 바뀐 항목이 없습니다. "
              "이미 목표 상태이거나 선택박스 조작이 먹히지 않은 것입니다.")

    if not click_selector(frame, SEL_APPLY_BTN, "변경 적용"):
        raise RuntimeError(
            f"변경 적용 버튼을 찾지 못했습니다 ({SEL_APPLY_BTN}). "
            "id 가 바뀐 것으로 보입니다. dump_screen.py 로 실제 id 를 확인하세요."
        )

    # 적용하면 확인 모달이 뜬다. 네이티브 alert 은 dialog 핸들러가 받지만
    # WebSquare 자체 모달은 직접 '확인'을 눌러야 실제로 저장된다.
    # (이걸 안 눌러서 아무것도 안 바뀌는 경우가 있다.)
    for _ in range(6):
        page.wait_for_timeout(500)
        if dismiss_ws_popup(page):
            print("  확인 모달 처리")
    page.wait_for_timeout(1000)
    return countof_disabled, countof_changed


def read_total(frame):
    """조회 결과의 총 항목수 / 총 페이지수를 읽는다."""
    total = int(frame.locator(SEL_TXT_TOTAL).first.inner_text())
    totalpage = int(frame.locator(SEL_TXT_TOTALPAGE).first.inner_text())
    return total, totalpage


def change_all_pages(frame, page):
    """현재 조회 결과의 모든 페이지를 TO_BE_CHANGED 로 변경한다.

    변경이 적용되면 해당 항목은 INQ_CONDITION 조건에서 빠지므로 목록이 줄어든다.
    그래서 기본 전략은 '첫 페이지를 계속 처리'이고, 페이지 전체가 선택불가일
    때만 다음 페이지로 넘어간다.
    """
    processed = 0
    stagnant = 0  # 총건수가 줄지 않은 연속 횟수 (무한루프 방지)
    prev_total = None

    while True:
        total, totalpage = read_total(frame)
        print(f"\n총 항목개수: {total} / 총 페이지: {totalpage}")

        if total == 0:
            print("더 이상 항목이 없으므로 종료!")
            break

        if prev_total is not None and total >= prev_total:
            stagnant += 1
            if stagnant >= 3:
                print(f"총건수가 3회 연속 줄지 않았습니다({total}건). "
                      "더 진행해도 변화가 없어 중단합니다.")
                break
        else:
            stagnant = 0
        prev_total = total

        countof_disabled, countof_changed = all_click_on_this_page(frame, page)
        processed += countof_changed

        if countof_changed == 0:
            # 이 페이지가 전부 선택불가 → 다음 페이지 시도
            nxt = frame.locator(SEL_NEXT_PAGE).first
            try:
                can_next = nxt.is_visible() and nxt.is_enabled()
            except Exception:
                can_next = False
            if can_next:
                print("이 페이지는 전부 선택불가 → 다음 페이지로 이동")
                click_selector(frame, SEL_NEXT_PAGE, "다음 페이지", 0.5)
            else:
                print(f"선택불가항목 {countof_disabled}건만 남아 종료합니다.")
                break

    print(f"\n=> 이번 조회에서 변경한 항목: {processed}건")
    return processed


def process_quarter(frame, page, year, qrt):
    """지정한 연도/분기를 조회한 뒤 전체를 TO_BE_CHANGED 로 변경한다."""
    print(f"\n{'=' * 55}")
    print(f"[{year} {qrt}] {INQ_CONDITION} → {TO_BE_CHANGED} 일괄 변경")
    print("=" * 55)

    select_quarterly(frame)
    frame.locator(SEL_SELECT_YEAR).first.select_option(label=year)
    frame.locator(SEL_SELECT_QRT).first.select_option(label=qrt)
    frame.locator(SEL_SELECT_COND).first.select_option(label=INQ_CONDITION)
    click_search(frame)

    return change_all_pages(frame, page)


def run_menu(page, frame):
    global INQ_CONDITION, TO_BE_CHANGED

    select_quarterly(frame)

    year_texts = [t.strip() for t in
                  frame.locator(SEL_SELECT_YEAR).first.locator("option").all_inner_texts()]
    qrt_texts = [t.strip() for t in
                 frame.locator(SEL_SELECT_QRT).first.locator("option").all_inner_texts()]
    menu_list = make_menu_list(year_texts, qrt_texts)

    while True:
        answer = show_menu("무엇을 도와드릴까요?", menu_list)

        if "항목 조회:" in answer:
            select_quarterly(frame)

            splited = answer.split(":")
            selected_year = splited[1].strip()
            selected_qrt = splited[2].strip()

            frame.locator(SEL_SELECT_YEAR).first.select_option(label=selected_year)
            frame.locator(SEL_SELECT_QRT).first.select_option(label=selected_qrt)
            frame.locator(SEL_SELECT_COND).first.select_option(label=INQ_CONDITION)

            click_search(frame)
            continue

        elif "조회대상 수정" in answer:
            INQ_CONDITION = "공제대상" if INQ_CONDITION == "불공제대상" else "불공제대상"
            menu_list = make_menu_list(year_texts, qrt_texts)
            continue

        elif "변경대상 수정" in answer:
            TO_BE_CHANGED = "공제" if TO_BE_CHANGED == "불공제" else "불공제"
            menu_list = make_menu_list(year_texts, qrt_texts)
            continue

        elif "일괄 변경" in answer:
            total = 0
            for year, qrt in BATCH_TARGETS:
                total += process_quarter(frame, page, year, qrt)
            print(f"\n### {len(BATCH_TARGETS)}개 분기 합계 변경: {total}건")
            continue

        elif "변경하기." in answer:
            change_all_pages(frame, page)
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
            # www.hometax.go.kr → WebSquare 메인으로 리다이렉트된다.
            # '전체메뉴' 버튼이 생길 때까지 기다려야 메인 화면이 다 뜬 것.
            page.wait_for_selector(SEL_ALL_MENU, timeout=30000)
            page.wait_for_timeout(1000)
            print(page.title())

            login(page)

            # 사업용신용카드 매입세액 공제 확인/변경 화면으로 이동
            goto_deduction_page(page)
            frame = open_work_context(page)

            # 분기별 → 조회 (기본 조회를 한 번 수행한 뒤 메뉴로 넘어간다)
            select_quarterly(frame)
            try:
                frame.locator(SEL_SELECT_COND).first.select_option(label=INQ_CONDITION)
            except Exception as e:
                print(f"조회대상({INQ_CONDITION}) 선택 생략: {e}")
            click_search(frame)

            run_menu(page, frame)
        except Exception as e:
            print(e)
        finally:
            input("종료하려면 Enter 를 누르세요...")
            browser.close()


if __name__ == "__main__":
    main()
