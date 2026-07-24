# 홈택스 자동화 v2 (Playwright)

2026 홈택스 개편(아이디 로그인 + 주민등록번호 본인확인)에 대응한 Playwright 버전입니다.
기존 pydoll 버전(`../hometax.go.kr/`)은 그대로 두고 새로 작성했습니다.

## 설치

```bash
pip install -r requirements.txt
# Playwright 자체 브라우저 대신 시스템 Chrome 을 쓰므로 별도 브라우저 설치는 불필요합니다.
# (Playwright 번들 브라우저를 쓰고 싶다면: python3 -m playwright install chromium)
```

## 실행

```bash
python3 hometax_playwright.py
```

## 로그인 흐름 (아이디 로그인)

1. 상단 **로그인** 클릭 → 로그인 페이지
2. **아이디 로그인** 탭 선택 (`[data-tab="login_tab3"]`)
3. 아이디(`iptUserId`) / 비밀번호(`iptUserPw`) 입력
4. 본인확인 **주민등록번호 앞 6자리 + 뒤 1자리** 입력 (입력창이 노출되면)
5. **로그인** 실행 (`a.logingbtn`)

주민번호 입력창은 조건부로 노출되므로, 아이디/비번 입력 직후와 로그인 클릭 후
두 시점 모두에서 표시 여부를 확인해 입력합니다.

## 설정 (`hometax_playwright.py` 상단)

| 변수 | 설명 |
|------|------|
| `LOGIN_ID` / `LOGIN_PW` | 홈택스 아이디 / 비밀번호 |
| `JUMIN_FRONT` | 주민등록번호 앞 6자리. 비워두면 실행 중 콘솔에서 입력받음 |
| `JUMIN_BACK` | 주민등록번호 뒤 1자리. 비워두면 실행 중 콘솔에서 입력받음 |
| `INQ_CONDITION` | 조회 대상(공제대상 / 불공제대상) |
| `TO_BE_CHANGED` | 변경 대상(공제 / 불공제) |

> 주민등록번호는 개인정보입니다. 코드에 직접 넣기보다 비워두고 실행 시 입력하는 것을 권장합니다.

## pydoll 버전과의 차이

- 비동기(async/await) → **동기(sync) Playwright API** 로 단순화
- 요소 탐색을 `locator` 기반으로 통일
- alert/confirm 은 `page.on("dialog", ...)` 로 자동 수락
- iframe(`#txppIframe`)은 `content_frame()` 으로 진입
- 로그인 판별을 "보이는 **로그아웃** 버튼 존재 여부"로 정확화
  (메인/로그인 페이지 안내문의 '로그아웃' 텍스트 오탐 방지)
