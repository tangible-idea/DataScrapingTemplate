# 홈택스 자동화 v2 (Playwright)

2026 홈택스 개편(아이디 로그인 + 주민등록번호 본인확인)에 대응한 Playwright 버전입니다.
기존 pydoll 버전(`../hometax.go.kr/`)은 그대로 두고 새로 작성했습니다.

## 설치

```bash
pip install -r requirements.txt
# Playwright 자체 브라우저 대신 시스템 Chrome 을 쓰므로 별도 브라우저 설치는 불필요합니다.
# (Playwright 번들 브라우저를 쓰고 싶다면: python3 -m playwright install chromium)
```

## 자격증명 설정

아이디·비밀번호·주민등록번호는 **코드에 넣지 않고 환경변수로** 전달합니다.

```bash
cp .env.example .env
# .env 를 열어 값 채우기
```

| 환경변수 | 설명 |
|----------|------|
| `HOMETAX_ID` | 홈택스 아이디 |
| `HOMETAX_PW` | 홈택스 비밀번호 |
| `HOMETAX_JUMIN_FRONT` | 2차 인증용 주민등록번호 앞 6자리 |
| `HOMETAX_JUMIN_BACK` | 2차 인증용 주민등록번호 뒤 1자리 |

- `.env` 는 `.gitignore` 에 등록되어 커밋되지 않습니다.
- 셸에서 `export` 한 값이 `.env` 보다 우선합니다.
- **비워두면 실행 중 콘솔에서 입력받습니다.** 비밀번호는 `getpass` 로 받아 화면에
  찍히지 않으므로, `.env` 에 비밀번호를 저장하지 않는 쪽이 더 안전합니다.
- 별도 패키지(`python-dotenv`) 없이 `load_dotenv()` 가 직접 읽습니다.

## 실행

```bash
python3 hometax_playwright.py
```

`.env` 없이 그때그때 넘기고 싶다면:

```bash
HOMETAX_ID=myid python3 hometax_playwright.py   # 나머지는 콘솔에서 입력
```

## 로그인 흐름 (아이디 로그인)

1. 상단 **로그인** 클릭 → 로그인 페이지
2. **아이디 로그인** 탭 선택 (`[data-tab="login_tab3"]`)
3. 아이디(`iptUserId`) / 비밀번호(`iptUserPw`) 입력
4. 본인확인 **주민등록번호 앞 6자리 + 뒤 1자리** 입력 (입력창이 노출되면)
5. **로그인** 실행 (`a.logingbtn`)

주민번호 입력창은 조건부로 노출되므로, 아이디/비번 입력 직후와 로그인 클릭 후
두 시점 모두에서 표시 여부를 확인해 입력합니다.

## 화면 이동 흐름

로그인 후 **`사업용신용카드 매입세액 공제 확인/변경`** 화면으로 직접 이동합니다
(`goto_deduction_page()`).

```
https://hometax.go.kr/websquare/websquare.html?w2xPath=/ui/pp/index_pp.xml
    &tmIdx=46&tm2lIdx=4608020000&tm3lIdx=4608020100
```

이 화면은 메뉴상 아래 경로에 해당합니다.

```
계산서·영수증·카드 → 신용카드 매입 → 사업용 신용카드 사용내역 → 매입세액 공제 확인/변경
```

**메뉴를 클릭해 들어가지 않고 URL 로 직접 들어가는 이유:** 메뉴 링크는
`href="javascript:void(0);"` + 핸들러 구조라 클릭 시 WebSquare 가 주소만 바꾸고
본문 로더를 제대로 태우지 않는 경우가 있습니다. 그러면 본문 iframe 이
`src="about:blank"` 인 채로 숨겨져 남아 화면을 못 찾습니다. 전체 페이지 로드로
들어가면 이 문제가 없습니다.

화면 진입 후 **분기별 → 조회**를 자동 수행합니다.

| 단계 | 셀렉터 | 비고 |
|------|--------|------|
| 분기별 | `#rdoSearch_input_2` → 라벨 `분기별` 폴백 | |
| 조회 | `#btnSearch` → `value="조회"` 폴백 | |

### 메뉴 클릭 경로 (예비)

URL 이 다시 바뀌면 `USE_MENU_NAVIGATION = True` 로 켜서 실제 메뉴를 클릭해
들어갈 수 있습니다. 셀렉터는 라이브 확인을 마쳤습니다.

| 단계 | 셀렉터 | 비고 |
|------|--------|------|
| 전체메뉴 | `a.btn_all[title="전체메뉴"]` | 상단 GNB 는 이 오버레이 안에만 있음 |
| 계산서·영수증·카드 | `//a[./span[text()="계산서·영수증·카드"]]` | 좌측 레일. id 가 uuid 라 텍스트로 탐색 |
| 신용카드 매입 | `#menuUl46_4608000000` | 기본 펼침 상태라 존재 확인만 |
| 사업용 신용카드 사용내역 | `#menuAtag_4608020000` | '+' 를 눌러 하위 메뉴 펼치기 |
| 매입세액 공제 확인/변경 | `#menuAtag_4608020100` | |

## 업무 화면 요소 id — `mf_txppWframe_` 접두사

**개편으로 업무 화면이 iframe 밖으로 나왔습니다.** 예전에는 모든 업무 화면이
`txppIframe` 안에 그려졌지만, 지금은 **메인 문서**에 직접 그려지고
`txppIframe` 은 `src="about:blank"` 인 빈 껍데기로 남습니다.
그리고 모든 요소 id 앞에 `mf_txppWframe_` 이 붙습니다.

| 개편 전 | 개편 후 |
|---------|---------|
| `#selectYear` | `#mf_txppWframe_selectYear` |
| `#selectQrt` | `#mf_txppWframe_selectQrt` |
| `#selectbox4` | `#mf_txppWframe_selectbox4` |
| `#rdoSearch_input_2` | `#mf_txppWframe_rdoSearch_input_2` |
| `#btnSearch` | `#mf_txppWframe_btnSearch` |
| `#pglNavi_next_btn` | `#mf_txppWframe_pglNavi_**nextPage**_btn` (이름도 바뀜) |

`wsel()` 헬퍼가 접두사 있는 id 와 없는 id 를 **둘 다** 매칭하는 셀렉터를 만들어
어느 쪽이든 동작합니다.

```python
wsel("selectYear")   # -> "#mf_txppWframe_selectYear, #selectYear"
```

`open_work_context()` 는 iframe 을 고정해 기다리지 않고, 조회 조건 요소가 실제로
있는 컨텍스트를 메인 문서 + 모든 프레임에서 찾습니다. 못 찾으면 프레임 구성을
진단 출력(`dump_frames()`)한 뒤 종료합니다.

### 화면 요소 id 조사하기 — `dump_screen.py`

개편으로 id 가 또 바뀌면 이 스크립트로 실제 id 를 확인할 수 있습니다.

```bash
python3 dump_screen.py
```

같은 로그인·이동 흐름을 탄 뒤 프레임 변화를 20초간 관찰하고, 프레임별로
`select`(옵션 포함) / `radio`(라벨 포함) / 버튼·링크의 실제 id 를 덤프합니다.

### 개편으로 바뀐 점 (실제 사이트 확인)

- **업무 화면이 iframe 밖으로 나오고 모든 id 에 `mf_txppWframe_` 접두사가 붙음**
  (위 표 참고). `txppIframe` 은 `about:blank` 인 빈 껍데기로 남습니다.
- **딥링크 URL 변경.** 개편 전 `websquare.wq?...&tmIdx=1&tm2lIdx=0105040000&tm3lIdx=0105040400`
  은 더 이상 동작하지 않고, 현재는
  `websquare.html?...&tmIdx=46&tm2lIdx=4608020000&tm3lIdx=4608020100` 입니다.
- **동명이의 메뉴 주의.** '매입세액 공제 확인/변경'은 '화물운전자 복지카드' 아래
  (`menuAtag_4608030100`)에도 같은 이름으로 존재하므로 반드시 메뉴코드로 구분해야 합니다.
- **안내 팝업이 네이티브 alert 이 아님.** 세션이 없으면 "로그인 정보가 없습니다."가
  WebSquare 자체 모달(`w2window`)로 뜨며 `page.on("dialog")` 로는 잡히지 않습니다.
  `dismiss_ws_popup()` 이 별도로 처리합니다.
- 전체메뉴 오버레이 항목은 애니메이션 탓에 Playwright 가 '보이지 않음'으로 판정하는
  경우가 많아, 일반 클릭 실패 시 `dispatch_event("click")` 으로 폴백합니다.

## 설정 (`hometax_playwright.py` 상단)

자격증명은 환경변수로 옮겼습니다(위 참고). 코드 상단에는 동작 옵션만 남았습니다.

| 변수 | 설명 |
|------|------|
| `INQ_CONDITION` | 조회 대상(공제대상 / 불공제대상) |
| `TO_BE_CHANGED` | 변경 대상(공제 / 불공제) |
| `USE_MENU_NAVIGATION` | `True` 면 URL 직접 이동 대신 메뉴를 클릭해서 진입 |

## pydoll 버전과의 차이

- 비동기(async/await) → **동기(sync) Playwright API** 로 단순화
- 요소 탐색을 `locator` 기반으로 통일
- alert/confirm 은 `page.on("dialog", ...)` 로 자동 수락하고,
  WebSquare 자체 모달은 `dismiss_ws_popup()` 이 따로 처리
- iframe 고정 대신 마커 요소로 업무 화면 컨텍스트를 탐색(`open_work_context()`)
- 로그인 판별을 "보이는 **로그아웃** 버튼 존재 여부"로 정확화
  (메인/로그인 페이지 안내문의 '로그아웃' 텍스트 오탐 방지)
- 자격증명을 소스에서 분리해 환경변수/`.env` 로 이동
