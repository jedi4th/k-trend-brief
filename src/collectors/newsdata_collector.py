"""
NewsData.io API 수집기
NewsData.io API를 통해 K-콘텐츠 관련 뉴스를 수집합니다.
(무료 API: 하루 100개)
"""
import requests
from typing import List, Dict
import time

from config import CATEGORIES, ITEMS_PER_SOURCE, REQUEST_TIMEOUT, NEWSDATA_API_KEY


class NewsDataCollector:
    """NewsData.io API 수집 클래스"""

    BASE_URL = "https://newsdata.io/api/1/latest"

    def __init__(self):
        self.api_key = NEWSDATA_API_KEY
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        if not self.api_key:
            print("⚠️ NewsData.io API 키가 설정되지 않았습니다.")
            print("   https://newsdata.io/ 에서 무료 API 키를 발급받을 수 있습니다.")
        else:
            print("✅ NewsData.io API 수집기 초기화 완료")

    def _create_news_dict(self, article: dict) -> Dict:
        """NewsData.io文章 데이터를 딕셔너리로 변환"""
        return {
            'title': article.get('title', ''),
            'link': article.get('link', ''),
            'description': article.get('description', '')[:200] if article.get('description') else "",
            'source': article.get('source_id', 'Unknown'),
            'pubDate': article.get('pubDate', ''),
            'image_url': article.get('image_url', ''),
            'category': article.get('category', [])
        }

    def collect_category(self, category: str, keywords: List[str]) -> List[Dict]:
        """카테고리별 뉴스 수집"""
        results = []

        if not self.api_key:
            return results

        # 키워드를 쉼표로 연결
        keywords_str = ','.join(keywords[:3])  # 최대 3개 키워드

        params = {
            'apikey': self.api_key,
            'q': keywords_str,
            'language': 'en',
            'category': 'entertainment,top',  # 문화 관련 카테고리
            'size': ITEMS_PER_SOURCE
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code != 200:
                print(f"⚠️ NewsData.io API 오류: {response.status_code}")
                return results

            data = response.json()

            if data.get('status') != 'success':
                print(f"⚠️ API 응답 오류: {data.get('results')}")
                return results

            articles = data.get('results', [])

            for article in articles:
                if len(results) >= ITEMS_PER_SOURCE:
                    break

                try:
                    news_dict = self._create_news_dict(article)

                    # 관련성 필터링 (키워드가 제목에 포함된 경우)
                    title_lower = news_dict['title'].lower()
                    if any(kw.lower() in title_lower for kw in keywords):
                        news_dict['category'] = category
                        results.append(news_dict)

                except Exception as e:
                    continue

        except requests.RequestException as e:
            print(f"⚠️ {category} 뉴스 수집 오류: {e}")

        return results

    def collect_all(self) -> Dict[str, List[Dict]]:
        """모든 카테고리 뉴스 수집"""
        all_news = {cat: [] for cat in CATEGORIES.keys()}

        if not self.api_key:
            print("📰 뉴스 수집 건너뜀 (API 키 없음)")
            return all_news

        print("\n📰 뉴스 API 수집 중...")

        for category, keywords in CATEGORIES.items():
            print(f"   → {category} 수집 중...")

            news_items = self.collect_category(category, keywords)

            # 중복 제거
            for news in news_items:
                if not any(n['link'] == news['link'] for n in all_news[category]):
                    all_news[category].append(news)

            # 상위 5개만 유지
            all_news[category] = all_news[category][:ITEMS_PER_SOURCE]

            # 요청 간격
            time.sleep(1)

        # 결과 요약
        total = sum(len(v) for v in all_news.values())
        print(f"   → 총 {total}개 뉴스 수집 완료")

        return all_news


if __name__ == "__main__":
    # 테스트 실행
    from config import NEWSDATA_API_KEY

    if NEWSDATA_API_KEY:
        collector = NewsDataCollector()
        test_news = collector.collect_category("K-POP", CATEGORIES["K-POP"])
        print("\n=== K-POP 뉴스 테스트 ===")
        for news in test_news[:3]:
            print(f"- {news['title']}")
            print(f"  출처: {news['source']}")
    else:
        print("API 키를 설정하세요: NEWSDATA_API_KEY")
