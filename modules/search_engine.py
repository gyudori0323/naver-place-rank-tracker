import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import urllib.parse

class NaverPlaceSearchEngine:
    """네이버 플레이스 검색 엔진 클래스"""
    
    def __init__(self, headless=True):
        """
        검색 엔진 초기화
        
        Args:
            headless (bool): 헤드리스 모드 사용 여부
        """
        self.logger = logging.getLogger("NaverPlaceSearchEngine")
        self.headless = headless
        self.driver = None
        
    def _setup_driver(self):
        """Selenium WebDriver 설정"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--log-level=3')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        
        # GitHub Actions에서 실행될 때 필요한 추가 옵션
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        return webdriver.Chrome(options=options)
    
    def build_url(self, keyword):
        """
        검색어를 기반으로 네이버 지도 검색 URL을 생성
        
        Args:
            keyword (str): 검색 키워드
            
        Returns:
            str: 검색 URL
        """
        encoded_keyword = urllib.parse.quote(keyword)
        return f"https://map.naver.com/p/search/{encoded_keyword}?searchType=place"
    
    def search(self, keyword, shop_name, max_scrolls=50):
        """
        키워드로 검색하여 특정 상호명의 순위를 찾음
        
        Args:
            keyword (str): 검색 키워드
            shop_name (str): 찾을 상호명
            max_scrolls (int): 최대 스크롤 횟수
            
        Returns:
            dict: 검색 결과 (순위, 성공 여부, 메시지 등)
        """
        result = {
            "keyword": keyword,
            "shop_name": shop_name,
            "rank": -1,
            "success": False,
            "message": "",
            "search_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            self.driver = self._setup_driver()
            url = self.build_url(keyword)
            self.driver.get(url)
            self.logger.info(f"URL: {url}")
            
            # iframe 로딩 대기 및 전환
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe"))
                )
            except TimeoutException:
                result["message"] = "iframe 로딩 시간 초과"
                self.logger.error(result["message"])
                return result
            
            # 검색 결과 컨테이너 로딩 대기
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.Ryr1F#_pcmap_list_scroll_container"))
                )
            except TimeoutException:
                self.driver.save_screenshot("error_screenshot.png")
                result["message"] = "페이지 로딩 실패 또는 검색 결과 없음"
                self.logger.error(result["message"])
                return result
            
            rank = 0
            found = False
            scroll_count = 0
            
            while not found and scroll_count < max_scrolls:
                scroll_count += 1
                self.logger.info(f"스크롤 횟수: {scroll_count}")
                
                # 현재 페이지 소스에서 상점 목록 추출
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                shop_list_element = soup.select("div.Ryr1F#_pcmap_list_scroll_container > ul > li")
                
                for shop_element in shop_list_element:
                    # 광고 요소 건너뛰기
                    ad_element = shop_element.select_one(".gU6bV._DHlh")
                    if ad_element:
                        continue
                    
                    rank += 1
                    shop_name_element = shop_element.select_one(".place_bluelink.tWIhh > span.O_Uah")
                    
                    if shop_name_element:
                        current_shop_name = shop_name_element.text.strip()
                        if current_shop_name == shop_name:
                            result["rank"] = rank
                            result["success"] = True
                            result["message"] = f"'{shop_name}'은(는) '{keyword}' 검색 결과에서 {rank}위입니다."
                            self.logger.info(result["message"])
                            found = True
                            break
                
                if found:
                    break
                
                # 다음 결과를 위해 스크롤
                self.driver.execute_script(
                    "document.querySelector('#_pcmap_list_scroll_container').scrollTo(0, document.querySelector('#_pcmap_list_scroll_container').scrollHeight)"
                )
                time.sleep(1)
            
            if not found:
                result["message"] = f"'{shop_name}'을(를) 찾을 수 없습니다."
                self.logger.warning(result["message"])
        
        except Exception as e:
            result["message"] = f"오류 발생: {type(e).__name__} - {e}"
            self.logger.error(result["message"])
        
        finally:
            if self.driver:
                self.driver.quit()
                
        return result
