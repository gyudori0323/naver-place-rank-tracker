import time
import logging
import requests
import urllib.parse
from bs4 import BeautifulSoup

class NaverPlaceSearchEngine:
    """네이버 플레이스 검색 엔진 클래스 (순수 requests/BeautifulSoup 사용)"""
    
    def __init__(self, headless=True):  # headless 파라미터 유지 (호환성)
        """검색 엔진 초기화"""
        self.logger = logging.getLogger("NaverPlaceSearchEngine")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://map.naver.com/"
        }
    
    def build_url(self, keyword) :
        """검색어를 기반으로 네이버 지도 검색 URL을 생성"""
        encoded_keyword = urllib.parse.quote(keyword)
        return f"https://map.naver.com/p/search/{encoded_keyword}?searchType=place"
    
    def search(self, keyword, shop_name, max_scrolls=50) :
        """
        키워드로 검색하여 특정 상호명의 순위를 찾음
        
        Args:
            keyword (str): 검색 키워드
            shop_name (str): 찾을 상호명
            max_scrolls (int): 사용하지 않음 (호환성 유지)
            
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
            # 검색 URL 생성
            url = self.build_url(keyword)
            self.logger.info(f"검색 URL: {url}")
            
            # 페이지 요청
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                result["message"] = f"페이지 요청 실패: 상태 코드 {response.status_code}"
                self.logger.error(result["message"])
                return result
            
            # HTML 파싱 (iframe 내용 직접 요청)
            soup = BeautifulSoup(response.text, "html.parser")  # lxml 대신 html.parser 사용
            
            # iframe URL 추출 시도
            iframe_src = None
            for iframe in soup.find_all("iframe"):
                if iframe.get("id") == "searchIframe":
                    iframe_src = iframe.get("src")
                    break
            
            if not iframe_src:
                # iframe URL을 찾을 수 없는 경우 추정
                iframe_src = f"https://pcmap.place.naver.com/place/list?query={urllib.parse.quote(keyword) }"
            
            # iframe 내용 요청
            iframe_response = requests.get(iframe_src, headers=self.headers)
            
            if iframe_response.status_code != 200:
                result["message"] = f"iframe 요청 실패: 상태 코드 {iframe_response.status_code}"
                self.logger.error(result["message"])
                return result
            
            # iframe 내용 파싱
            iframe_soup = BeautifulSoup(iframe_response.text, "html.parser")  # lxml 대신 html.parser 사용
            
            # 장소 목록 찾기 (여러 선택자 시도)
            place_items = iframe_soup.select("div.Ryr1F#_pcmap_list_scroll_container > ul > li")
            
            if not place_items:
                place_items = iframe_soup.select("li.VLTHu")  # 대체 선택자
            
            if not place_items:
                place_items = iframe_soup.select("li.UEzoS")  # 또 다른 대체 선택자
            
            if not place_items:
                result["message"] = "장소 목록을 찾을 수 없습니다."
                self.logger.error(result["message"])
                return result
            
            # 장소 순위 찾기
            rank = 0
            for item in place_items:
                # 광고 건너뛰기
                ad_element = item.select_one(".gU6bV._DHlh")
                if ad_element:
                    continue
                
                rank += 1
                
                # 상점명 찾기 (여러 선택자 시도)
                shop_name_element = item.select_one(".place_bluelink.tWIhh > span.O_Uah")
                
                if not shop_name_element:
                    shop_name_element = item.select_one("span.place_bluelink")
                
                if not shop_name_element:
                    shop_name_element = item.select_one("span.TYaxT")
                
                if shop_name_element:
                    current_shop_name = shop_name_element.get_text().strip()
                    if current_shop_name == shop_name:
                        result["rank"] = rank
                        result["success"] = True
                        result["message"] = f"'{shop_name}'은(는) '{keyword}' 검색 결과에서 {rank}위입니다."
                        self.logger.info(result["message"])
                        return result
            
            # 찾지 못한 경우
            result["message"] = f"'{shop_name}'을(를) 찾을 수 없습니다."
            self.logger.warning(result["message"])
            
        except Exception as e:
            result["message"] = f"오류 발생: {type(e).__name__} - {e}"
            self.logger.error(result["message"])
        
        return result
