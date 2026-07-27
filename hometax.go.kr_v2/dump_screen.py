# -*- coding: utf-8 -*-
#
# 업무 화면 DOM 진단 스크립트.
#
# hometax_playwright.py 와 똑같은 로그인/이동 흐름을 탄 뒤,
# 도착한 화면에 실제로 존재하는 요소(select / radio / 버튼)의 id 를 덤프한다.
# 홈택스 개편으로 id 가 바뀌었을 때 무엇으로 교체해야 하는지 확인하는 용도.
#
#   python3 dump_screen.py
#
# 자격증명은 hometax_playwright.py 와 동일하게 .env 에서 읽는다.

import json
import time

from playwright.sync_api import sync_playwright

import hometax_playwright as H


# 각 프레임에서 실행해 폼 요소를 수집하는 스크립트.
COLLECT_JS = """
() => {
  const pick = (el) => ({
    tag: el.tagName,
    id: el.id || null,
    name: el.getAttribute('name') || null,
    title: el.getAttribute('title') || null,
    visible: el.offsetParent !== null,
  });
  const selects = [...document.querySelectorAll('select')].map(s => Object.assign(pick(s), {
    options: [...s.options].map(o => (o.text || '').trim()).slice(0, 12),
  }));
  const radios = [...document.querySelectorAll('input[type=radio]')].map(r => {
    const lab = r.id ? document.querySelector('label[for="' + r.id + '"]') : null;
    return Object.assign(pick(r), {
      label: lab ? (lab.textContent || '').trim().slice(0, 20) : null,
      value: (r.value || '').slice(0, 20),
    });
  });
  const buttons = [...document.querySelectorAll(
      'input[type=button],input[type=submit],button,a[class*=btn],a[id*=btn]')]
    .map(b => Object.assign(pick(b), {
      text: ((b.value || b.textContent || '').trim()).slice(0, 20),
    }))
    .filter(b => b.text && b.visible)
    .slice(0, 60);
  // '조회' 처럼 우리가 찾는 텍스트를 가진 요소는 따로 뽑아둔다.
  const wanted = ['조회', '분기별', '반기별', '전체선택', '변경', '적용'];
  const matches = [...document.querySelectorAll('input,button,a,label')]
    .map(e => Object.assign(pick(e), {
      text: ((e.value || e.textContent || '').trim()).slice(0, 20),
    }))
    .filter(e => wanted.some(w => e.text === w))
    .slice(0, 40);
  return {
    url: location.href.slice(0, 100),
    bodyLen: document.body ? document.body.innerText.length : 0,
    idCount: document.querySelectorAll('[id]').length,
    selects, radios, buttons, matches,
  };
}
"""


def show(label, rows, keys):
    print(f"\n  [{label}] {len(rows)}개")
    for r in rows:
        print("    " + "  ".join(f"{k}={r.get(k)!r}" for k in keys if r.get(k) is not None))


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, channel="chrome",
            args=["--disable-popup-blocking", "--start-maximized"],
        )
        page = browser.new_context(no_viewport=True).new_page()
        page.on("dialog", lambda d: d.accept())

        try:
            page.goto(H.BASE_URL)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_selector(H.SEL_ALL_MENU, timeout=30000)
            page.wait_for_timeout(1000)

            H.login(page)
            H.goto_deduction_page(page)

            # 본문이 늦게 그려질 수 있으므로 프레임 구성이 안정될 때까지 지켜본다.
            print("\n=== 프레임 변화 관찰 (5초 간격 x 4회) ===")
            for i in range(4):
                page.wait_for_timeout(5000)
                frames = [(f.name, f.url[:60]) for f in page.frames]
                print(f"  {(i + 1) * 5:2d}초: 프레임 {len(frames)}개 -> {frames}")
                H.dismiss_ws_popup(page)

            print("\n=== 프레임별 폼 요소 덤프 ===")
            for f in page.frames:
                try:
                    data = f.evaluate(COLLECT_JS)
                except Exception as e:
                    print(f"\n[프레임 name={f.name!r}] 평가 실패: {e}")
                    continue
                print(f"\n[프레임 name={f.name!r}] url={data['url']!r}")
                print(f"  본문 텍스트 길이={data['bodyLen']}  id 보유 요소={data['idCount']}")
                if data["bodyLen"] == 0 and data["idCount"] == 0:
                    print("  (빈 프레임)")
                    continue
                show("select", data["selects"], ["id", "name", "visible", "options"])
                show("radio", data["radios"], ["id", "name", "label", "value", "visible"])
                show("텍스트 일치(조회/분기별/전체선택 등)", data["matches"],
                     ["tag", "id", "name", "text", "visible"])
                show("버튼/링크", data["buttons"], ["tag", "id", "text"])

            print("\n=== 요약: 기존 마커 존재 여부 ===")
            for marker in H.SEL_WORK_MARKERS:
                where = [f.name or "(메인)" for f in page.frames
                         if _safe_count(f, marker) > 0]
                print(f"  {marker:22s} -> {where or '없음'}")

        except Exception as e:
            print(f"\n오류: {e}")
        finally:
            input("\n브라우저를 닫으려면 Enter... (F12 로 직접 확인해도 됩니다)")
            browser.close()


def _safe_count(frame, selector):
    try:
        return frame.locator(selector).count()
    except Exception:
        return 0


if __name__ == "__main__":
    main()
