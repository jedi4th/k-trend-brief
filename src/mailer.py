"""
이메일 발송 모듈
Jinja2 템플릿을 사용하여 HTML 이메일을 생성하고 SMTP로 발송합니다.
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from jinja2 import Template
from typing import Dict, List

from config import SMTP_SERVER, SMTP_PORT, GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENTS, CATEGORY_ICONS


class EmailMailer:
    """이메일 발송 클래스"""

    def __init__(self, template_path: str = "templates/newsletter.html"):
        self.template_path = template_path
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.sender_email = GMAIL_USER
        self.sender_password = GMAIL_APP_PASSWORD

        # 카테고리 아이콘 매핑 (config에서 가져오기)
        self.category_icons = CATEGORY_ICONS

    def _load_template(self) -> Template:
        """HTML 템플릿 로드"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            return Template(template_content)
        except FileNotFoundError:
            print(f"⚠️ 템플릿 파일을 찾을 수 없습니다: {self.template_path}")
            raise

    def _organize_data(self, news: Dict, reddit: Dict, youtube: Dict) -> Dict:
        """데이터를 카테고리별로 정리"""
        organized = {}

        categories = list(CATEGORY_ICONS.keys())

        for category in categories:
            organized[category] = {
                'news': news.get(category, []),
                'reddit': reddit.get(category, []),
                'youtube': youtube.get(category, [])
            }

        return organized

    def render_html(self, news: Dict, reddit: Dict, youtube: Dict) -> str:
        """HTML 이메일 렌더링"""
        template = self._load_template()

        # 데이터 정리
        newsletter_data = self._organize_data(news, reddit, youtube)

        # 오늘 날짜
        today = datetime.now().strftime("%Y년 %m월 %d일 %A")

        # HTML 렌더링
        html_content = template.render(
            newsletter=newsletter_data,
            category_icons=self.category_icons,
            date=today
        )

        return html_content

    def send_email(self, html_content: str, subject: str = None) -> bool:
        """이메일 발송"""
        if not self.sender_email or not self.sender_password:
            print("⚠️ 이메일 설정이 완료되지 않았습니다.")
            print("   .env 파일에서 GMAIL_USER와 GMAIL_APP_PASSWORD를 설정하세요.")
            return False

        # 제목 설정
        if subject is None:
            today = datetime.now().strftime("%Y-%m-%d")
            subject = f"[K-Trend Brief] {today} K-콘텐츠 트렌드"

        # 수신자 설정
        recipients = [r.strip() for r in RECIPIENTS if r.strip()]
        if not recipients:
            print("⚠️ 수신자가 설정되지 않았습니다.")
            print("   .env 파일에서 RECIPIENTS를 설정하세요.")
            return False

        try:
            # 이메일 메시지 생성
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = ", ".join(recipients)

            # HTML 콘텐츠 추가
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # SMTP 연결 및 발송
            context = ssl.create_default_context()

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)  # TLS 암호화
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipients, message.as_string())

            print(f"✅ 이메일 발송 성공!")
            print(f"   수신자: {', '.join(recipients)}")
            print(f"   제목: {subject}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("⚠️ Gmail 인증 실패")
            print("   앱 비밀번호를 확인하세요. (2단계 인증 후 생성)")
            return False
        except smtplib.SMTPException as e:
            print(f"⚠️ 이메일 발송 실패: {e}")
            return False
        except Exception as e:
            print(f"⚠️ 예상치 못한 오류: {e}")
            return False


if __name__ == "__main__":
    # 테스트 실행
    print("📧 이메일 모듈 테스트")
    mailer = EmailMailer()

    # 샘플 데이터로 HTML 생성 테스트
    sample_news = {
        "K-POP": [{"title": "테스트 뉴스", "link": "https://example.com", "source": "BBC", "pubDate": "2024-01-01"}]
    }
    sample_reddit = {
        "K-POP": [{"title": "테스트 Reddit", "link": "https://reddit.com", "subreddit": "kpop", "upvotes": 100, "comments": 50}]
    }
    sample_youtube = {
        "K-POP": [{"title": "테스트 YouTube", "link": "https://youtube.com", "views": 10000, "thumbnail": ""}]
    }

    print("\n📝 HTML 생성 테스트:")
    html = mailer.render_html(sample_news, sample_reddit, sample_youtube)
    print(f"   HTML 길이: {len(html)} 자")
    print("   (실제 발송은 send_email() 호출 필요)")
