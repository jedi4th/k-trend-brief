"""
뉴스레터 메인 실행 파일
Reddit, NewsData.io, YouTube에서 데이터를 수집하여 HTML 파일로 저장합니다.
"""
import os
from datetime import datetime
from collectors import RedditCollector, NewsDataCollector, YouTubeCollector
from config import CATEGORIES


def main():
    print("=" * 50)
    print("🚀 K-Trend Daily Brief 시작")
    print("=" * 50)

    # 1. Reddit 수집
    print("\n📊 데이터 수집 중...")
    print("\n📱 Reddit 수집 중...")
    reddit_collector = RedditCollector()
    reddit_data = reddit_collector.collect_all()

    # 2. NewsData.io API 수집
    print("\n📰 NewsData.io API 수집 중...")
    news_collector = NewsDataCollector()
    news_data = news_collector.collect_all()

    # 3. YouTube RSS 수집
    print("\n📺 YouTube RSS 수집 중...")
    youtube_collector = YouTubeCollector()
    youtube_data = youtube_collector.collect_all()

    # 4. HTML 생성
    print("\n🎨 HTML 생성 중...")
    from mailer import EmailMailer
    mailer = EmailMailer()
    html_content = mailer.render_html(news_data, reddit_data, youtube_data)

    # 5. HTML 파일로 저장
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    output_filename = os.path.join(output_dir, f"k_trend_brief_{datetime.now().strftime('%Y%m%d')}.html")
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n✅ 완료! HTML 파일이 생성되었습니다: {output_filename}")

    # 요약 출력
    print("\n📋 수집 요약:")
    for category in CATEGORIES.keys():
        n_news = len(news_data.get(category, []))
        n_reddit = len(reddit_data.get(category, []))
        n_youtube = len(youtube_data.get(category, []))
        print(f"  {category}: 📰 {n_news} | 📱 {n_reddit} | 📺 {n_youtube}")

    # 총계
    total_news = sum(len(v) for v in news_data.values())
    total_reddit = sum(len(v) for v in reddit_data.values())
    total_youtube = sum(len(v) for v in youtube_data.values())
    print(f"\n📈 총계: 📰 {total_news} | 📱 {total_reddit} | 📺 {total_youtube}")

    return output_filename


if __name__ == "__main__":
    main()
