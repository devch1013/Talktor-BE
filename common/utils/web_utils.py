import io
import tempfile
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class WebUtils:
    """웹 관련 유틸리티"""

    @staticmethod
    def get_page_title(url: str) -> str:
        """
        웹페이지의 제목을 가져옵니다.

        Args:
            url: 웹페이지 URL

        Returns:
            str: 웹페이지 제목. 실패 시 URL을 반환
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("title")

            if title and title.string:
                return title.string.strip()

            return url
        except Exception as e:
            print(f"Failed to get page title from {url}: {str(e)}")
            return url

    @staticmethod
    def capture_screenshot(url: str) -> Optional[io.BytesIO]:
        """
        웹페이지의 스크린샷을 촬영합니다.

        Args:
            url: 웹페이지 URL

        Returns:
            io.BytesIO: 스크린샷 이미지 데이터 (PNG 형식). 실패 시 None
        """
        try:
            with sync_playwright() as p:
                # Chromium 브라우저 실행 (headless 모드)
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    viewport={"width": 1280, "height": 720}  # 스크린샷 크기 설정
                )

                # 페이지 로드
                page.goto(url, wait_until="networkidle", timeout=30000)

                # 스크린샷 촬영
                screenshot_bytes = page.screenshot(type="png", full_page=False)

                browser.close()

                # BytesIO로 변환하여 반환
                return io.BytesIO(screenshot_bytes)

        except Exception as e:
            print(f"Failed to capture screenshot from {url}: {str(e)}")
            return None

    @staticmethod
    def get_page_info(url: str) -> Tuple[str, Optional[io.BytesIO]]:
        """
        웹페이지의 제목과 스크린샷을 모두 가져옵니다.

        Args:
            url: 웹페이지 URL

        Returns:
            Tuple[str, Optional[io.BytesIO]]: (페이지 제목, 스크린샷 이미지 데이터)
        """
        title = WebUtils.get_page_title(url)
        screenshot = WebUtils.capture_screenshot(url)
        return title, screenshot
