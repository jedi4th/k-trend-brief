"""
설정 파일
카테고리, 소스, API 설정 등을 관리합니다.
"""
import os
from dotenv import load_dotenv

# .env 파일 로드 (로컬 테스트용)
load_dotenv()

# ============================================
# 카테고리 설정
# ============================================
CATEGORIES = {
    "K-CULTURE": ["korean culture", "korea travel", "korean tradition", "seoul travel"],
    "K-POP": ["k-pop", "bts", "blackpink", "korean idol", "kpop news"],
    "K-DRAMA": ["k-drama", "korean drama", "netflix korea", "korean series"],
    "K-FOOD": ["korean food", "kimchi", "korean street food", "bts food"],
    "K-BEAUTY": ["k-beauty", "korean skincare", "korean makeup", "olive young"]
}

CATEGORY_ICONS = {
    "K-CULTURE": "🎨",
    "K-POP": "🎵",
    "K-DRAMA": "📺",
    "K-FOOD": "🍜",
    "K-BEAUTY": "💄"
}

# ============================================
# Reddit 설정 (무료 - API 키 불필요)
# ============================================
SUBREDDITS = {
    "K-CULTURE": ["r/Korea", "r/koreatravel", "r/korean"],
    "K-POP": ["r/kpop", "r/kpopthoughts", "r/bts", "r/blackpink"],
    "K-DRAMA": ["r/kdrama", "r/KDRAMA", "r/netflixkorean"],
    "K-FOOD": ["r/koreanfood", "r/KoreanFood"],
    "K-BEAUTY": ["r/AsianBeauty", "r/KoreanBeauty"]
}

# ============================================
# NewsData.io API 설정 (무료)
# https://newsdata.io/ 에서 API 키 발급 가능
# 무료 플랜: 하루 100개 뉴스
# ============================================
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")

# NewsData.io 지원 언어/국가
NEWSDATA_LANGUAGES = ["en", "ko"]
NEWSDATA_COUNTRIES = ["us", "gb", "fr", "de", "br"]

# ============================================
# YouTube RSS 설정
# ============================================
YOUTUBE_CHANNELS = {
    "K-CULTURE": [
        "UC4I7u-9_5G-0gKjK8g5J5zA",  # Korean travel
    ],
    "K-POP": [
        "UC2pmfLm7iq6Ov1UwYrWYkZA",  # KBS KPOP
        "UCO1J7R1D1H2fUK2BNFoei6g",  # M2
    ],
    "K-DRAMA": [
        "UC4R5Yp3eZvMxq2LeexeB4Qg",  # K-Drama
    ],
    "K-FOOD": [
        "UC3g8-a4JZ1J5J5J5J5J5J5A",  # Korean food
    ],
    "K-BEAUTY": [
        "UC5D8a8-5G-0gKjK8g5J5zA",  # K-Beauty
    ]
}

# YouTube 검색 키워드 (RSS가 실패할 경우 사용)
YOUTUBE_SEARCH_KEYWORDS = {
    "K-CULTURE": ["korean culture", "korea travel vlog", "seoul travel"],
    "K-POP": ["kpop 2024", "bts new song", "blackpink official"],
    "K-DRAMA": ["k-drama 2024", "korean drama review", "netflix korea"],
    "K-FOOD": ["korean food Mukbang", "korean street food", "kimchi making"],
    "K-BEAUTY": ["korean skincare routine", "korean makeup tutorial", "olive young"]
}

# ============================================
# 수집 설정
# ============================================
ITEMS_PER_SOURCE = 5  # 각 소스에서 가져올 항목 수
REQUEST_TIMEOUT = 10  # HTTP 요청 타임아웃 (초)

# ============================================
# 이메일 설정 (Gmail SMTP)
# ============================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECIPIENTS = os.getenv("RECIPIENTS", "").split(",")

# ============================================
# 출력 설정
# ============================================
OUTPUT_DIR = "output"
