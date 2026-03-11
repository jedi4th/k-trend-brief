"""
YouTube 수집기
yt-dlp 라이브러리를 통해 K-콘텐츠 관련 인기 영상을 수집합니다.
(API 키 불필요)
"""
import yt_dlp
from typing import List, Dict
import time

from config import CATEGORIES, YOUTUBE_SEARCH_KEYWORDS, ITEMS_PER_SOURCE


class YouTubeCollector:
    """YouTube yt-dlp 수집 클래스"""

    def __init__(self):
        # yt-dlp 옵션 설정
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,  # 상세 정보 추출
            'ignoreerrors': True,
            'nocheckcertificate': True,
        }
        print("✅ YouTube yt-dlp 수집기 초기화 완료")

    def _create_video_dict(self, video_info: dict) -> Dict:
        """YouTube 비디오 데이터를 딕셔너리로 변환"""
        # 썸네일 URL (여러 해상도 중 첫 번째 사용)
        thumbnail = ""
        if 'thumbnail' in video_info:
            thumbnails = video_info.get('thumbnails', [])
            if thumbnails:
                thumbnail = thumbnails[0].get('url', '')

        # 조회수
        views = video_info.get('view_count', 0)

        # 업로드 날짜
        upload_date = video_info.get('upload_date', '')
        if upload_date:
            # YYYYMMDD 형식을 보기 좋게 변환
            try:
                upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
            except:
                upload_date = ''

        # 설명 (길이 제한)
        description = video_info.get('description', '')
        if description:
            description = description[:200].replace('\n', ' ')

        return {
            'title': video_info.get('title', ''),
            'video_id': video_info.get('id', ''),
            'link': f"https://www.youtube.com/watch?v={video_info.get('id', '')}",
            'published': upload_date,
            'views': views,
            'description': description,
            'thumbnail': thumbnail,
            'channel': video_info.get('channel', ''),
            'duration': video_info.get('duration', 0),
            'likes': video_info.get('like_count', 0)
        }

    def search_videos(self, keywords: List[str], max_results: int = 10) -> List[Dict]:
        """유튜브 검색을 통해 영상 수집"""
        results = []

        # 검색 쿼리 생성
        search_query = ' '.join(keywords[:2])  # 최대 2개 키워드

        try:
            ydl = yt_dlp.YoutubeDL(self.ydl_opts)

            # YouTube에서 검색
            search_url = f"ytsearch{max_results}:{search_query}"

            info = ydl.extract_info(search_url, download=False)

            if info and 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        try:
                            video_dict = self._create_video_dict(entry)
                            results.append(video_dict)
                        except Exception as e:
                            continue

        except Exception as e:
            print(f"   ⚠️ 검색 오류 ({search_query}): {e}")

        return results

    def collect_category(self, category: str) -> List[Dict]:
        """카테고리별 YouTube 영상 수집"""
        results = []

        # 검색 키워드
        keywords = YOUTUBE_SEARCH_KEYWORDS.get(category, [])

        if not keywords:
            return results

        # 검색어로 영상 검색
        videos = self.search_videos(keywords, max_results=ITEMS_PER_SOURCE * 2)

        # 중복 제거 및 필터링
        seen_ids = set()
        for video in videos:
            if video['video_id'] in seen_ids:
                continue
            seen_ids.add(video['video_id'])

            # 키워드 관련성 확인
            title_lower = video['title'].lower()
            desc_lower = video['description'].lower()

            if any(kw.lower() in title_lower or kw.lower() in desc_lower for kw in keywords):
                results.append(video)

            if len(results) >= ITEMS_PER_SOURCE:
                break

        # 조회수순 정렬
        results = sorted(results, key=lambda x: x['views'], reverse=True)

        return results[:ITEMS_PER_SOURCE]

    def collect_all(self) -> Dict[str, List[Dict]]:
        """모든 카테고리 YouTube 영상 수집"""
        all_videos = {cat: [] for cat in CATEGORIES.keys()}

        print("\n📺 YouTube yt-dlp 수집 중...")

        for category in CATEGORIES.keys():
            print(f"   → {category} 검색 중...")
            videos = self.collect_category(category)
            all_videos[category] = videos
            print(f"   → {category}: {len(videos)}개 수집 완료")

            # 요청 간격 (API 제한 방지)
            time.sleep(1)

        return all_videos


if __name__ == "__main__":
    # 테스트 실행
    collector = YouTubeCollector()
    test_videos = collector.collect_category("K-POP")
    print("\n=== K-POP YouTube 테스트 ===")
    for video in test_videos[:3]:
        print(f"- {video['title']}")
        print(f"  조회수: {video['views']:,}")
        print(f"  채널: {video['channel']}")
