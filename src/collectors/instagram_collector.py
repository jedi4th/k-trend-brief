"""
Instagram 수집기
웹 스크래핑을 통해 K-콘텐츠 관련 게시물을 수집합니다.
(제한적 작동 - Instagram의 강화된 방어로 인해 실패할 수 있음)
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import re

from config import CATEGORIES, ITEMS_PER_SOURCE


class InstagramCollector:
    """Instagram 스크래핑 수집 클래스"""

    # 검색할 해시태그
    HASHTAGS = {
        "K-CULTURE": ["koreanculture", "koreatravel", "seoul"],
        "K-POP": ["kpop", "bts", "blackpink", "kpopfashion"],
        "K-DRAMA": ["kdrama", "koreandrama", "netflixkorea"],
        "K-FOOD": ["koreanfood", "kimchi", "koreanstreetfood"],
        "K-BEAUTY": ["kbeauty", "koreanskincare", "koreanmakeup"]
    }

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        print("✅ Instagram 수집기 초기화 완료")
        print("   참고: Instagram은 스크래핑을 막아서 로컬에서도 작동하지 않을 수 있습니다.")

    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""
        # 해시태그/멘션 유지하되 정리
        text = ' '.join(text.split())
        return text[:150]

    def fetch_hashtag(self, hashtag: str) -> List[Dict]:
        """인스타그램 해시태그 페이지에서 게시물 가져오기"""
        results = []

        try:
            # 인스타그램 해시태그 URL (웹 버전)
            url = f"https://www.instagram.com/explore/tags/{hashtag}/"

            response = requests.get(url, headers=self.headers, timeout=15)

            if response.status_code != 200:
                print(f"   ⚠️ 요청 실패: {response.status_code}")
                return results

            # JSON 데이터 추출 시도
            soup = BeautifulSoup(response.text, 'html.parser')

            # script 태그에서 JSON 데이터 찾기
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'window._sharedData' in script.string:
                    try:
                        # JSON 파싱
                        json_str = script.string.replace('window._sharedData = ', '').rstrip(';')
                        data = json.loads(json_str)

                        # 게시물 데이터 추출
                        if 'entry_data' in data and 'TagPage' in data['entry_data']:
                            media = data['entry_data']['TagPage'][0].get('graphql', {}).get('hashtag', {}).get('edge_hashtag_to_media', {}).get('edges', [])

                            for item in media[:ITEMS_PER_SOURCE]:
                                node = item.get('node', {})
                                results.append({
                                    'title': self._clean_text(node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', '')),
                                    'link': f"https://www.instagram.com/p/{node.get('shortcode', '')}/",
                                    'thumbnail': node.get('thumbnail_src', ''),
                                    'likes': node.get('edge_liked_by', {}).get('count', 0),
                                    'comments': node.get('edge_media_to_comment', {}).get('count', 0),
                                    'username': '',
                                    'date': ''
                                })

                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        print(f"   ⚠️ 데이터 파싱 오류: {e}")

        except requests.RequestException as e:
            print(f"   ⚠️ 네트워크 오류: {e}")

        return results

    def collect_category(self, category: str) -> List[Dict]:
        """카테고리별 Instagram 게시물 수집"""
        results = []

        hashtags = self.HASHTAGS.get(category, [])

        if not hashtags:
            return results

        # 각 해시태그로 검색
        for hashtag in hashtags[:2]:  # 최대 2개
            posts = self.fetch_hashtag(hashtag)

            for post in posts:
                if post['link'] not in [p['link'] for p in results]:
                    results.append(post)

            time.sleep(1)  # 요청 간격

        return results[:ITEMS_PER_SOURCE]

    def collect_all(self) -> Dict[str, List[Dict]]:
        """모든 카테고리 Instagram 게시물 수집"""
        all_posts = {cat: [] for cat in CATEGORIES.keys()}

        print("\n📸 Instagram 수집 중...")

        for category in CATEGORIES.keys():
            posts = self.collect_category(category)
            all_posts[category] = posts
            print(f"   → {category}: {len(posts)}개 수집 완료")

        return all_posts


if __name__ == "__main__":
    # 테스트 실행 (거의 작동 안 함)
    collector = InstagramCollector()
    test_posts = collector.collect_category("K-POP")
    print("\n=== K-POP Instagram 테스트 ===")
    if test_posts:
        for post in test_posts[:3]:
            print(f"- {post['title']}")
    else:
        print("   Instagram 스크래핑은 현재 제한되어 있습니다.")
