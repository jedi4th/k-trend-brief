# K-Trend Daily Brief

매일 아침 해외 언론사, Reddit에서 K-콘텐츠 트렌드를 수집하여 이메일로 보내주는 뉴스레터 자동화 프로젝트입니다.

## 지원 카테고리

- K-CULTURE (한국 문화)
- K-POP (케이팝)
- K-DRAMA (한국 드라마)
- K-FOOD (한국 음식)
- K-BEAUTY (한국 뷰티)

## 데이터 소스

- **해외언론사**: Google News RSS (영미권 뉴스)
- **Reddit**: r/kpop, r/kdrama, r/KoreanFood, r/KBeauty 등 (API 키 불필요)

## 특징

- **API 키 불필요**: Reddit은 공개 JSON API를 사용하므로 별도 API 키가 필요 없습니다
- **무료**: 모든 기능이 무료로 작동합니다
- **자동화**: GitHub Actions로 매일 아침 자동 실행

## 설치 방법

1. 리포지토리를 클론합니다

```bash
git clone https://github.com/yourusername/k-trend-brief.git
cd k-trend-brief
```

2. 가상환경을 생성하고 활성화합니다

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성을 설치합니다

```bash
pip install -r requirements.txt
```

4. `.env` 파일을 생성하고 설정합니다

```env
# Gmail 설정 (필수)
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
RECIPIENTS=your-email@gmail.com
```

## 로컬 실행

```bash
cd src
python main.py
```

실행 후 `k_trend_brief_YYYYMMDD.html` 파일이 생성됩니다.

## GitHub Secrets 설정

GitHub 리포지토리의 `Settings` → `Secrets and variables` → `Actions`에서 다음 Secret을 추가합니다:

| Secret 이름 | 값 |
|-------------|---|
| `GMAIL_USER` | Gmail 주소 (예: `user@gmail.com`) |
| `GMAIL_APP_PASSWORD` | Gmail 앱 비밀번호 |
| `RECIPIENTS` | 수신자 이메일 |

## 자동화

GitHub Actions가 설정되어 있어 매일 한국 시간 아침 7시(UTC 22시)에 자동으로 실행됩니다.

수동으로 실행하려면 GitHub 리포지토리의 `Actions` 탭에서 `Daily K-Trend Newsletter` 워크플로를 선택하고 `Run workflow`를 클릭합니다.

## Gmail 앱 비밀번호 생성 방법

1. [Google 계정](https://myaccount.google.com)으로 이동합니다
2. **보안** 탭 → 2단계 인증을 활성화합니다
3. 앱 비밀번호를 생성합니다:
   - 앱 선택: "메일"
   - 기기 선택: "기타" → 이름 입력: "K-Trend-Brief"
4. 생성된 16자리 비밀번호를 `GMAIL_APP_PASSWORD`로 사용

## 라이선스

MIT License
