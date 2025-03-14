# search_engine.py 파일을 다음과 같이 수정
import time
import logging
import asyncio
from requests_html import AsyncHTMLSession

class NaverPlaceSearchEngine:
    """네이버 플레이스 검색 엔진 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger("NaverPlaceSearchEngine")
        
    def build_url(self, keyword):
        """검색어를 기반으로 네이버 지도 검색 URL을 생성"""
        import urllib.parse
        encoded_keyword = urllib.parse.quote(keyword)
        return f"https://map.naver.com/p/search/{encoded_keyword}?searchType=place"
    
    async def _search_async(self, keyword, shop_name, max_scrolls=50) :
        session = AsyncHTMLSession()
        url = self.build_url(keyword)
        
        # 페이지 로드
        response = await session.get(url)
        await response.html.arender(sleep=3)  # JavaScript 실행 대기
        
        # iframe 전환 (JavaScript로 iframe 내용 가져오기)
        iframe_content = await response.html.render(script="""
            () => {
                const iframe = document.getElementById('searchIframe');
                if (iframe && iframe.contentDocument) {
                    return iframe.contentDocument.documentElement.outerHTML;
                }
                return null;
            }
        """)
        
        if not iframe_content:
            return {"success": False, "message": "iframe을 찾을 수 없습니다."}
        
        # BeautifulSoup 대신 requests-html의 파싱 기능 사용
        rank = 0
        found = False
        
        for scroll_count in range(max_scrolls):
            # 스크롤 실행
            await response.html.render(script="""
                () => {
                    const iframe = document.getElementById('searchIframe');
                    if (iframe && iframe.contentDocument) {
                        const container = iframe.contentDocument.querySelector('#_pcmap_list_scroll_container');
                        if (container) {
                            container.scrollTo(0, container.scrollHeight);
                            return true;
                        }
                    }
                    return false;
                }
            """)
            
            await asyncio.sleep(1)  # 스크롤 후 대기
            
            # 현재 페이지의 상점 목록 파싱
            shops_html = await response.html.render(script="""
                () => {
                    const iframe = document.getElementById('searchIframe');
                    if (iframe && iframe.contentDocument) {
                        const shops = Array.from(iframe.contentDocument.querySelectorAll('#_pcmap_list_scroll_container > ul > li'));
                        return shops.map(shop => shop.outerHTML);
                    }
                    return [];
                }
            """)
            
            # 각 상점 확인
            for shop_html in shops_html:
                # 광고 건너뛰기
                if 'gU6bV._DHlh' in shop_html:
                    continue
                    
                rank += 1
                
                # 상점명 확인
                shop_name_match = re.search(r'<span class="O_Uah">(.*?)</span>', shop_html)
                if shop_name_match and shop_name_match.group(1) == shop_name:
                    return {
                        "success": True,
                        "rank": rank,
                        "message": f"'{shop_name}'은(는) '{keyword}' 검색 결과에서 {rank}위입니다.",
                        "search_time": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
        
        # 찾지 못한 경우
        return {
            "success": False,
            "rank": -1,
            "message": f"'{shop_name}'을(를) 찾을 수 없습니다.",
            "search_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def search(self, keyword, shop_name, max_scrolls=50):
        """키워드로 검색하여 특정 상호명의 순위를 찾음"""
        try:
            # 비동기 함수 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._search_async(keyword, shop_name, max_scrolls))
            loop.close()
            return result
        except Exception as e:
            self.logger.error(f"오류 발생: {type(e).__name__} - {e}")
            return {
                "success": False,
                "rank": -1,
                "message": f"오류 발생: {type(e).__name__} - {e}",
                "search_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
