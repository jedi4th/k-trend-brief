"""
YouTube 수집기 (GitHub Actions 호환)
RSS 피드를 통해 K-콘텐츠 관련 영상을 수집합니다.
"""
import requests
from typing import List, Dict
import time
import xml.etree.ElementTree as ET
import re

from config import CATEGORIES, YOUTUBE_SEARCH_KEYWORDS, ITEMS_PER_SOURCE


class YouTubeCollector:
    """YouTube RSS 수집 클래스 - GitHub Actions 호환"""

    # 공개 K-Pop/K-Drama 채널 RSS
    CHANNEL_RSS = {
        "K-POP": [
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCtvrQYA4m4W6g9NNa3lJLiw",  # KBS World K-POP
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCO1J7R1D1H2fUK2BNFoei6g",  # M2
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC2Pm5C0tU3Ln54E7DCTLR5g",  # THE K-POP
        ],
        "K-DRAMA": [
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC4R5Yp3eZvMxq2LeexeB4Qg",  # K-Drama World
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC4I7u-9_5G-0gKjK8g5J5zA",  # KDrama
        ],
        "K-CULTURE": [
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC5D8a8-5G-0gKjK8g5J5zA",  # Korea
        ],
        "K-FOOD": [
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC3g8-a4JZ1J5J5J5J5J5J5A",  # Korean Food
        ],
        "K-BEAUTY": [
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC9PjOd9z-5G-0gKjK8g5J5zA",  # K-Beauty
        ]
    }

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml',
        }
        print("✅ YouTube RSS 수집기 초기화 완료")

    def _extract_video_info(self, entry) -> Dict:
        """RSS 항목에서 비디오 정보 추출"""
        # 비디오 ID 추출
        video_id = entry.find('id')
        video_id_text = video_id.text if video_id is not None else ''
        if 'video:' in video_id_text:
            video_id_text = video_id_text.split(':')[-1]

        # 제목
        title = entry.find('{http://www.w3.org/2005/Atom}title')
        title_text = title.text if title is not None else ''

        # 링크
        link = entry.find('{http://www.w3.org/2005/Atom}link')
        link_href = link.get('href') if link is not None else f"https://www.youtube.com/watch?v={video_id_text}"

        #published
        published = entry.find('{http://www.w3.org/2005/Atom}published')
        published_text = published.text[:10] if published is not None else ''  # YYYY-MM-DD

        #author
        author = entry.find('{http://www.w3.org/2005/Atom}author')
        channel_name = author.find('{http://www.w3.org/2005/Atom}name').text if author is not None else 'YouTube'

        return {
            'title': title_text,
            'video_id': video_id_text,
            'link': link_href,
            'published': published_text,
            'views': 0,  # RSS에는 조회수 없음
            'description': '',
            'thumbnail': f"https://img.youtube.com/vi/{video_id_text}/mqdefault.jpg",
            'channel': channel_name,
            'duration': 0,
            'likes': 0
        }

    def fetch_rss(self, rss_url: str) -> List[Dict]:
        """RSS 피드에서 영상 목록 가져오기"""
        results = []

        try:
            response = requests.get(rss_url, headers=self.headers, timeout=15)

            if response.status_code != 200:
                return results

            # XML 파싱
            root = ET.fromstring(response.content)

            # 항목 찾기
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

            for entry in entries[:10]:  # 최대 10개
                try:
                    video_info = self._extract_video_info(entry)
                    results.append(video_info)
                except Exception:
                    continue

        except Exception as e:
            print(f"   ⚠️ RSS 오류: {e}")

        return results

    def collect_category(self, category: str) -> List[Dict]:
        """카테고리별 YouTube 영상 수집"""
        results = []
        keywords = YOUTUBE_SEARCH_KEYWORDS.get(category, [])

        # RSS 피드에서 가져오기
        rss_urls = self.CHANNEL_RSS.get(category, [])

        for rss_url in rss_urls:
            videos = self.fetch_rss(rss_url)

            for video in videos:
                # 키워드 필터링
                title_lower = video['title'].lower()

                if keywords and any(kw.lower() in title_lower for kw in keywords):
                    if video['video_id'] not in [v['video_id'] for v in results]:
                        results.append(video)

                # 키워드가 없으면 모두 추가
                elif not keywords:
                    if video['video_id'] not in [v['video_id'] for v in results]:
                        results.append(video)

            time.sleep(0.5)  # 요청 간격

        return results[:ITEMS_PER_SOURCE]

    def collect_all(self) -> Dict[str, List[Dict]]:
        """모든 카테고리 YouTube 영상 수집"""
        all_videos = {cat: [] for cat in CATEGORIES.keys()}

        print("\n📺 YouTube RSS 수집 중...")

        for category in CATEGORIES.keys():
            videos = self.collect_category(category)
            all_videos[category] = videos
            print(f"   → {category}: {len(videos)}개 수집 완료")

        return all_videos


if __name__ == "__main__":
    collector = YouTubeCollector()
    test_videos = collector.collect_category("K-POP")
    print("\n=== K-POP YouTube 테스트 ===")
    for video in test_videos[:3]:
        print(f"- {video['title']}")
        print(f"  채널: {video['channel']}")
