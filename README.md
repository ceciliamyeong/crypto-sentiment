# 📊 Crypto Sentiment Indicator

소셜 데이터(Twitter/X, Reddit, 뉴스)를 수집해 크립토 시장 센티멘트를 지표화하는 파이프라인입니다.

## 지표 구조

```
소셜 데이터 수집 → 감성 분석 (VADER + 크립토 사전) → 영향력 가중 평균 → 점수 (-100 ~ +100)
```

| 점수 구간 | 상태 |
|-----------|------|
| 60 ~ 100 | 🟢 극도의 탐욕 |
| 20 ~ 59  | 🟡 탐욕 |
| -19 ~ 19 | ⚪ 중립 |
| -59 ~ -20 | 🟠 공포 |
| -100 ~ -60 | 🔴 극도의 공포 |

## 소스별 가중치

| 소스 | 가중치 | 이유 |
|------|--------|------|
| Twitter/X | 40% | 실시간 반응 가장 빠름 |
| Reddit | 35% | 깊이 있는 논의 |
| 뉴스 | 25% | 공신력 |

## 설치

```bash
pip install -r requirements.txt
```

## API 키 설정

`.env` 파일 생성 후 아래 내용 입력:

```env
TWITTER_BEARER_TOKEN=your_token_here
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here
NEWSAPI_KEY=your_key_here        # 없으면 RSS 자동 사용
```

- Twitter: https://developer.twitter.com
- Reddit: https://www.reddit.com/prefs/apps
- NewsAPI: https://newsapi.org (무료 플랜 가능)

## 실행

```bash
python main.py
```

## 프로젝트 구조

```
crypto-sentiment/
├── main.py              # 실행 진입점
├── requirements.txt
├── collector/
│   ├── twitter.py       # Twitter/X 수집
│   ├── reddit.py        # Reddit 수집
│   └── news.py          # 뉴스/RSS 수집
├── indicator/
│   └── sentiment.py     # 지표 알고리즘
├── api/                 # FastAPI 서버 (예정)
└── dashboard/           # React 프론트 (예정)
```

## 다음 단계

- [ ] `api/` — FastAPI로 지표 API 서버화
- [ ] `dashboard/` — React 대시보드 연결
- [ ] 시계열 저장 (PostgreSQL / SQLite)
- [ ] 스케줄러로 주기적 수집 자동화
