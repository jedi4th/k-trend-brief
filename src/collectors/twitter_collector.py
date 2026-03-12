"""
Twitter(X) 수집기
snscrape를 통해 K-콘텐츠 관련 트윗을 수집합니다.
(로컬에서만 작동 - GitHub Actions에서는 제한됨)
"""
import subprocess
import json
import re
from typing import List, Dict
import time

from config import CATEGORIES, ITEMS_PER_SOURCE


class TwitterCollector:
    """Twitter(X) snscrape 수집 클래스"""

    # 검색할 키워드
    SEARCH_KEYWORDS = {
        "K-CULTURE": ["korean culture", "korea travel", "seoul"],
        "K-POP": ["kpop", "bts", "blackpink", "korean idol"],
        "K-DRAMA": ["kdrama", "korean drama", "netflix korea"],
        "K-FOOD": ["korean food", "kimchi", "bts food"],
        "K-BEAUTY": ["kbeauty", "korean skincare", "korean makeup"]
    }

    def __init__(self):
        # snscrape 설치 확인
        try:
            subprocess.run(['snscrape', '--version'], capture_output=True, check=True)
            self.snscrape_available = True
            print("✅ Twitter(X) snscrape 수집기 초기화 완료")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.snscrape_available = False
            print("⚠️ snscrape가 설치되지 않았습니다.")
            print("   설치: pip install snscrape")
            print("   참고: GitHub Actions에서는 작동하지 않을 수 있습니다.")

    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""
        # URL 제거
        text = re.sub(r'http\S+', '', text)
        # 이모지/특수문자 정리
        text = ' '.join(text.split())
        return text[:200]

    def search_tweets(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """트윗 검색"""
        results = []

        if not self.snscrape_available:
            return results

        try:
            # snscrape로 트위터 검색
            cmd = [
                'snscrape',
                '--jsonl',
                '--max-results', str(max_results),
                f'twitter-search "{keyword} lang:en"'
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for line in process.stdout:
                try:
                    tweet = json.loads(line)

                    results.append({
                        'title': self._clean_text(tweet.get('content', '')),
                        'link': f"https://twitter.com/i/web/status/{tweet.get('id', '')}",
                        'username': tweet.get('user', {}).get('username', ''),
                        'upvotes': tweet.get('likeCount', 0),
                        'comments': tweet.get('replyCount', 0),
                        'date': tweet.get('date', '')[:10] if tweet.get('date') else '',
                        'description': self._clean_text(tweet.get('content', ''))
                    })

                except json.JSONDecodeError:
                    continue

            process.wait(timeout=30)

        except subprocess.TimeoutExpired:
            print(f"   ⚠️ 검색 시간 초과: {keyword}")
        except Exception as e:
            print(f"   ⚠️ 검색 오류 ({keyword}): {e}")

        return results

    def collect_category(self, category: str) -> List[Dict]:
        """카테고리별 트윗 수집"""
        results = []

        keywords = self.SEARCH_KEYWORDS.get(category, [])

        if not keywords:
            return results

        # 각 키워드로 검색
        for keyword in keywords[:2]:  # 최대 2개 키워드
            tweets = self.search_tweets(keyword, max_results=ITEMS_PER_SOURCE)

            for tweet in tweets:
                # 중복 제거
                if not any(t['link'] == tweet['link'] for t in results):
                    results.append(tweet)

            time.sleep(1)  # 요청 간격

        return results[:ITEMS_PER_SOURCE]

    def collect_all(self) -> Dict[str, List[Dict]]:
        """모든 카테고리 트윗 수집"""
        all_tweets = {cat: [] for cat in CATEGORIES.keys()}

        if not self.snscrape_available:
            print("\n🐦 Twitter(X) 수집 건너뜀 (snscrape 없음)")
            return all_tweets

        print("\n🐦 Twitter(X) snscrape 수집 중...")

        for category in CATEGORIES.keys():
            tweets = self.collect_category(category)
            all_tweets[category] = tweets
            print(f"   → {category}: {len(tweets)}개 수집 완료")

        return all_tweets


if __name__ == "__main__":
    # 테스트 실행
    collector = TwitterCollector()
    if collector.snscrape_available:
        test_tweets = collector.collect_category("K-POP")
        print("\n=== K-POP Twitter 테스트 ===")
        for tweet in test_tweets[:3]:
            print(f"- {tweet['title']}")
            print(f"  @{tweet['username']} ❤️ {tweet['upvotes']}")
