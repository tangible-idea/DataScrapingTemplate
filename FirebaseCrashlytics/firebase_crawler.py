#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Firebase Crashlytics Console Crawler

This script uses Playwright to log into Firebase Console Crashlytics using Google authentication.
"""

import os
import time
import asyncio
import argparse
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()


class FirebaseCrawler:
    """A class to handle Firebase Console Crashlytics web crawling using Playwright."""

    def __init__(self, headless=False):
        """Initialize the Firebase crawler.

        Args:
            headless (bool): Whether to run browser in headless mode
        """
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        """Start the browser session."""
        try:
            # Launch playwright and chromium browser
            self.playwright = await async_playwright().start()
            
            # User agent and viewport settings to mimic a real browser
            ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            
            # Browser launch options
            browser_options = {
                "headless": self.headless,
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-site-isolation-trials"
                ]
            }
            
            self.browser = await self.playwright.chromium.launch(**browser_options)
            
            # Context options with more realistic browser fingerprint
            context_options = {
                "user_agent": ua,
                "viewport": {"width": 1920, "height": 1080},
                "screen": {"width": 1920, "height": 1080},
                "device_scale_factor": 1,
                "is_mobile": False,
                "has_touch": False,
                "locale": "ko-KR",
                "timezone_id": "Asia/Seoul",
                "geolocation": {"longitude": 126.9780, "latitude": 37.5665},
                "permissions": ["geolocation"],
                "color_scheme": "light",
                "accept_downloads": True,
            }
            
            self.context = await self.browser.new_context(**context_options)
            
            # Bypass automated browser detection scripts
            await self.context.add_init_script("\
                Object.defineProperty(navigator, 'webdriver', {\
                    get: () => false\
                });\
                Object.defineProperty(navigator, 'plugins', {\
                    get: () => [1, 2, 3, 4, 5]\
                });\
            ")
            
            self.page = await self.context.new_page()
            print("브라우저 시작 성공")
        except Exception as e:
            print(f"브라우저 시작 실패: {str(e)}")
            raise

    async def open_firebase_crashlytics(self, url):
        """Open Firebase Crashlytics console.

        Args:
            url (str): Firebase Crashlytics URL
        """
        try:
            print(f"Firebase Crashlytics URL 열기: {url}")
            await self.page.goto(url, wait_until="domcontentloaded")
            print("URL 로드 완료")
        except Exception as e:
            print(f"URL 열기 실패: {str(e)}")
            raise

    async def login_with_google(self, email, password):
        """Login to Google account.

        Args:
            email (str): Google account email
            password (str): Google account password

        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            print(f"Google 계정으로 로그인 시도 중: {email}")
            
            # 이메일 입력 대기 및 입력
            print("이메일 입력 대기 중...")
            await self.page.wait_for_selector('input[type="email"], input#identifierId', state="visible", timeout=30000)
            
            # 이메일 입력 필드 찾기
            email_input = await self.page.query_selector('input[type="email"], input#identifierId')
            if not email_input:
                print("이메일 입력 필드를 찾을 수 없습니다.")
                return False
            
            # 이메일 입력
            await email_input.fill(email)
            print("이메일 입력 완료")
            
            # 잠시 대기 (자연스럽게 타이핑하는 효과)
            await asyncio.sleep(1.5)
            
            # 스크린샷 찍기 (이메일 입력 후)
            await self.page.screenshot(path="login_email.png")
            print("이메일 입력 후 스크린샷 저장: login_email.png")
            
            # Enter 키로 진행 시도
            try:
                await self.page.press('input[type="email"], input#identifierId', 'Enter')
                print("Enter 키 입력으로 진행 시도")
                await asyncio.sleep(2)  # Enter 키 누른 후 잠시 대기
            except Exception as e:
                print(f"Enter 키 입력 실패: {str(e)}")
            
                # 다음 버튼 클릭
                await asyncio.sleep(1.5)  # 잠시 대기
                print("'다음' 버튼 클릭 시도...")
            
            # 다양한 '다음' 버튼 선택자 시도
            next_button_selectors = [
                "#identifierNext > div > button",
                "div#identifierNext",
                "#identifierNext",
                "button[jsname='LgbsSe']",
                "div[role='button']:not([aria-disabled='true'])",
                "div.VfPpkd-RLmnJb",
                "#identifierNext > div > button > span"
            ]
            
            # 선택자별로 시도
            clicked = False
            for selector in next_button_selectors:
                try:
                    print(f"선택자 시도: {selector}")
                    # 선택자 존재 여부 확인
                    is_visible = await self.page.is_visible(selector)
                    print(f"  선택자 표시 여부: {is_visible}")
                    
                    if is_visible:
                        await self.page.click(selector, timeout=5000)
                        print(f"  '{selector}' 버튼 클릭 성공")
                        clicked = True
                        await asyncio.sleep(2)  # 클릭 후 잠시 대기
                        break
                except Exception as e:
                    print(f"  선택자 '{selector}' 클릭 실패: {str(e)}")
            
            # 스크린샷 찍기 (다음 버튼 클릭 후)
            await self.page.screenshot(path="login_next.png")
            print("다음 버튼 클릭 후 스크린샷 저장: login_next.png")
            
            # 보안 경고 페이지 여부 확인
            security_error = await self.page.query_selector("text=This browser or app may not be secure")
            if security_error:
                print("Google 보안 경고 발견: 브라우저 자동화 감지")
                
                # 보안 경고 페이지 스크린샷
                await self.page.screenshot(path="security_warning.png")
                print("보안 경고 페이지 스크린샷 저장: security_warning.png")
                
                # 사용자에게 수동 로그인 메시지 표시
                print("자동 로그인이 차단되었습니다. 수동 작업이 필요합니다.")
                print("30초 동안 유지한 후 Firebase Console 접속을 시도합니다...")
                
                # 사용자가 수동으로 로그인할 시간 제공
                for i in range(30, 0, -1):
                    print(f"수동 로그인을 완료해주세요... {i}초 남음", end="\r")
                    await asyncio.sleep(1)
                    
                # 30초 후 Firebase 콘솔 접속 시도
                print("직접 Firebase Crashlytics 콘솔에 접속 시도 중...")
                await self.open_firebase_crashlytics("https://console.firebase.google.com/u/1/project/nxshlife/crashlytics/")
                
                # Firebase 콘솔 접속 확인
                try:
                    await self.page.wait_for_selector(".project-header, .firebase-logo", timeout=10000)
                    print("Firebase 콘솔 접속 성공!")
                    await self.page.screenshot(path="firebase_console.png")
                    return True
                except Exception as e:
                    print(f"Firebase 콘솔 접속 실패: {str(e)}")
                    return False
            
            # 비밀번호 입력 대기
            print("비밀번호 입력 필드 대기 중...")
            try:
                await self.page.wait_for_selector('input[type="password"]', state="visible", timeout=15000)
                
                # 비밀번호 입력
                password_input = await self.page.query_selector('input[type="password"]')
                if not password_input:
                    print("비밀번호 입력 필드를 찾을 수 없습니다.")
                    return False
                
                # 비밀번호 입력 전에 잠시 대기 (너무 빠른 입력 방지)
                await asyncio.sleep(1.5)
                
                # 비밀번호 입력
                await password_input.fill(password)
                print("비밀번호 입력 완료")
                
                # 다음 버튼 클릭 (비밀번호 입력 후)
                print("비밀번호 '다음' 버튼 클릭 중...")
                await self.page.click("button[jsname='LgbsSe'], #passwordNext button, div[role='button']:not([aria-disabled='true'])")
                print("비밀번호 '다음' 버튼 클릭 완료")
                
                # 로그인 완료 확인
                print("로그인 완료 확인 중...")
                try:
                    # Firebase 콘솔 로드 대기
                    await self.page.wait_for_selector(".project-header, .firebase-logo", timeout=15000)
                    await self.page.screenshot(path="login_success.png")
                    print("Firebase Console에 성공적으로 로그인했습니다!")
                    return True
                except Exception as e:
                    print(f"Firebase 콘솔 확인 실패: {str(e)}")
                    current_url = self.page.url
                    print(f"현재 URL: {current_url}")
                    
                    if "project/nxshlife/crashlytics" in current_url:
                        print("Firebase 콘솔에 접속 성공!")
                        return True
                    
                    return False
                
            except Exception as e:
                print(f"비밀번호 필드 로딩 또는 입력 실패: {str(e)}")
                
                # 스크린샷 찍기 (비밀번호 화면 로딩 실패)
                await self.page.screenshot(path="password_error.png")
                print("비밀번호 화면 로딩/입력 실패 스크린샷 저장: password_error.png")
                
                # 현재 URL 확인
                current_url = self.page.url
                print(f"현재 URL: {current_url}")
                
                if "project/nxshlife/crashlytics" in current_url:
                    print("이미 Firebase 콘솔에 로그인되어 있습니다!")
                    return True
                
                return False
                
        except Exception as e:
            print(f"로그인 프로세스 실패: {str(e)}")
            return False
        finally:
            pass  # 프로세스 완료 후 필요한 클린업 작업이 있다면 여기에 추가

    async def take_screenshot(self, filename):
        """Take a screenshot of the current page.

        Args:
            filename (str): Path to save the screenshot
        """
        try:
            await self.page.screenshot(path=filename)
            print(f"스크린샷 저장 완료: {filename}")
        except Exception as e:
            print(f"스크린샷 저장 실패: {str(e)}")

    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            print("브라우저 종료")


async def main_async(email, password, url, headless):
    """Async main function."""
    crawler = None
    try:
        # 크롤러 초기화
        crawler = FirebaseCrawler(headless=headless)
        await crawler.start()
        
        # Firebase Crashlytics 콘솔 열기
        await crawler.open_firebase_crashlytics(url)
        
        # Google 계정으로 로그인
        success = await crawler.login_with_google(email, password)
        
        if success:
            # 로그인 성공 시 스크린샷 저장
            await crawler.take_screenshot("firebase_console.png")
            print("로그인 성공! 브라우저는 계속 열려 있습니다. Ctrl+C로 종료하세요.")
            
            # 브라우저를 열어둔 상태로 유지
            while True:
                await asyncio.sleep(1)
        else:
            print("로그인 실패")
    
    except KeyboardInterrupt:
        print("프로그램 종료 중...")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
    finally:
        # 종료 시 브라우저 닫기
        if crawler:
            await crawler.close()


def main():
    """Main function to run the Firebase Crashlytics crawler."""
    parser = argparse.ArgumentParser(description="Firebase Crashlytics Console Crawler")
    parser.add_argument(
        "--email", 
        type=str, 
        default=os.getenv("GOOGLE_EMAIL"), 
        help="Google account email"
    )
    parser.add_argument(
        "--password", 
        type=str, 
        default=os.getenv("GOOGLE_PASSWORD"), 
        help="Google account password"
    )
    parser.add_argument(
        "--url", 
        type=str, 
        default="https://console.firebase.google.com/u/1/project/nxshlife/crashlytics/", 
        help="Firebase Crashlytics URL"
    )
    parser.add_argument(
        "--headless", 
        action="store_true", 
        help="Run browser in headless mode"
    )
    
    args = parser.parse_args()
    
    # 필수 인자 검증
    if not args.email or not args.password:
        print("오류: Google 이메일과 비밀번호가 필요합니다.")
        print("명령줄 인자로 제공하거나 다음 환경 변수를 설정하세요:")
        print("GOOGLE_EMAIL 및 GOOGLE_PASSWORD")
        return
    
    # 비동기 메인 함수 실행
    asyncio.run(main_async(args.email, args.password, args.url, args.headless))


if __name__ == "__main__":
    main()
