"""
실행 진입점
python main.py
"""
import os
from indicator import SentimentIndicator, plot_sentiment

# API 키 설정 (환경변수 또는 직접 입력)
indicator = SentimentIndicator(
    twitter_token  = os.getenv("TWITTER_BEARER_TOKEN", "YOUR_TOKEN"),
    reddit_id      = os.getenv("REDDIT_CLIENT_ID",     "YOUR_ID"),
    reddit_secret  = os.getenv("REDDIT_CLIENT_SECRET", "YOUR_SECRET"),
    news_api_key   = os.getenv("NEWSAPI_KEY",           ""),        # 없으면 RSS 사용
)

# 단일 코인
result = indicator.calculate("BTC")
print(f"\n  [{result['coin']}] {result['score']:+.1f}점  {result['label_ko']}")
print(f"  소스별: {result['source_scores']}")

# 전체 코인 + 시각화
# df = indicator.calculate_all()
# plot_sentiment(df)
