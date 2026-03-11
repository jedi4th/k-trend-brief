"""
Reddit 수집기
Reddit 공개 JSON API를 통해 K-콘텐츠 관련 인기 게시물을 수집합니다.
(API 키 없이 작동)
"""
import requests
from typing import List, Dict
import time

from config import CATEGORIES, SUBREDDITS, ITEMS_PER_SOURCE, REQUEST_TIMEOUT


class RedditCollector:
    """Reddit 수집 클래스 (API 키 불필요)"""

    def __init__(self):
        self.base_url = "https://www.reddit.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        print("✅ Reddit 수집기 초기화 완료 (API 키 불필요)")

    def _create_post_dict(self, post_data: dict) -> Dict:
        """Reddit 게시물 데이터를 딕셔너리로 변환"""
        data = post_data.get('data', {})

        return {
            'title': data.get('title', ''),
            'link': f"https://reddit.com{data.get('permalink', '')}",
            'upvotes': data.get('ups', 0),
            'comments': data.get('num_comments', 0),
            'subreddit': data.get('subreddit', ''),
            'preview': data.get('selftext', '')[:150] if data.get('selftext') else "",
            'created': data.get('created_utc', 0)
        }

    def collect_subreddit(self, subreddit_name: str, keywords: List[str]) -> List[Dict]:
        """특정 서브레딧에서 키워드 관련 게시물 수집"""
        results = []

        # r/ 제거
        subreddit = subreddit_name.replace('r/', '').lower()

        try:
            # Hot 게시물 가져오기
            url = f"{self.base_url}/r/{subreddit}/hot.json?limit=25"
            response = requests.get(url, headers=self.headers, timeout=REQUEST_TIMEOUT)

            if response.status_code != 200:
                print(f"⚠️ r/{subreddit} 요청 실패: {response.status_code}")
                return []

            data = response.json()
            posts = data.get('data', {}).get('children', [])

            for post in posts:
                if len(results) >= ITEMS_PER_SOURCE:
                    break

                try:
                    post_dict = self._create_post_dict(post)
                    title_lower = post_dict['title'].lower()
                    preview_lower = post_dict['preview'].lower()

                    # 키워드 확인
                    if any(kw.lower() in title_lower or kw.lower() in preview_lower for kw in keywords):
                        post_dict['category'] = self._get_category_for_subreddit(subreddit)
                        results.append(post_dict)

                except Exception as e:
                    continue

        except requests.RequestException as e:
            print(f"⚠️ r/{subreddit} 수집 오류: {e}")

        return results

    def _get_category_for_subreddit(self, subreddit_name: str) -> str:
        """서브레딧 이름을 카테고리로 매핑"""
        mapping = {
            "kpop": "K-POP", "bts": "K-POP", "blackpink": "K-POP", "kpopthoughts": "K-POP",
            "kdrama": "K-DRAMA", "koreantv": "K-DRAMA",
            "koreanfood": "K-FOOD", "food": "K-FOOD",
            "kbeauty": "K-BEAUTY", "skincareaddiction": "K-BEAUTY", "asianbeauty": "K-BEAUTY",
            "korea": "K-CULTURE", "korean": "K-CULTURE"
        }

        return mapping.get(subreddit_name.lower(), "K-CULTURE")

    def collect_all(self) -> Dict[str, List[Dict]]:
        """모든 카테고리 Reddit 게시물 수집"""
        all_posts = {cat: [] for cat in CATEGORIES.keys()}

        for category, subreddits in SUBREDDITS.items():
            print(f"📱 {category} Reddit 수집 중...")

            for subreddit in subreddits:
                posts = self.collect_subreddit(subreddit, CATEGORIES[category])
                for post in posts:
                    # 중복 제거
                    if not any(p['link'] == post['link'] for p in all_posts[category]):
                        all_posts[category].append(post)

                time.sleep(1)  # 요청 간격 (서버 부하 방지)

            # 상위 5개만 유지
            all_posts[category] = sorted(
                all_posts[category],
                key=lambda x: x['upvotes'],
                reverse=True
            )[:ITEMS_PER_SOURCE]

            print(f"   → {len(all_posts[category])}개 수집 완료")

        return all_posts


if __name__ == "__main__":
    # 테스트 실행
    collector = RedditCollector()
    test_posts = collector.collect_subreddit("kpop", CATEGORIES["K-POP"])
    print("\n=== K-POP Reddit 테스트 ===")
    for post in test_posts:
        print(f"- {post['title']}")
        print(f"  ↑ {post['upvotes']} 💬 {post['comments']}")
