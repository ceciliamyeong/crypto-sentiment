from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CC_KEY = os.environ.get("CRYPTOCOMPARE_API_KEY")
SAN_KEY = os.environ.get("SANTIMENT_API_KEY")

SANTIMENT_URL = "https://api.santiment.net/graphql"

SLUGS = [
    "bitcoin", "ethereum", "solana", "binance-coin",
    "xrp", "dogecoin", "cardano", "avalanche", "chainlink", "polkadot"
]

# Reddit 서브레딧 목록 (크립토 + 금융)
SUBREDDITS = [
    "CryptoCurrency", "Bitcoin", "ethereum", "investing",
    "finance", "wallstreetbets", "stocks", "economy"
]

# ── 뉴스 API (CryptoCompare) ──────────────────────────────────
@app.get("/api/news")
async def get_news():
    if not CC_KEY:
        return {"error": "CRYPTOCOMPARE_API_KEY not set"}
    url = f"https://min-api.cryptocompare.com/data/v2/news/?lang=EN&api_key={CC_KEY}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=10)
        return r.json()

# ── 코인 소셜 데이터 (Santiment) ───────────────────────────────
@app.get("/api/coins")
async def get_coins():
    if not SAN_KEY:
        return {"error": "SANTIMENT_API_KEY not set"}

    headers = {"Authorization": f"Apikey {SAN_KEY}"}
    results = []

    async with httpx.AsyncClient() as client:
        for slug in SLUGS:
            query = """
            {
              projectBySlug(slug: "%s") {
                name
                ticker
                socialVolume24h: aggregatedTimeseriesData(
                  metric: "social_volume_total"
                  from: "utc_now-1d"
                  to: "utc_now"
                  aggregation: SUM
                )
                socialVolume7d: aggregatedTimeseriesData(
                  metric: "social_volume_total"
                  from: "utc_now-7d"
                  to: "utc_now"
                  aggregation: SUM
                )
                sentiment: aggregatedTimeseriesData(
                  metric: "sentiment_balance_total"
                  from: "utc_now-1d"
                  to: "utc_now"
                  aggregation: AVG
                )
              }
            }
            """ % slug

            r = await client.post(
                SANTIMENT_URL,
                json={"query": query},
                headers=headers,
                timeout=15
            )
            data = r.json()
            if "errors" in data:
                continue

            project_list = data.get("data", {}).get("projectBySlug", [])
            if not project_list:
                continue

            p = project_list[0] if isinstance(project_list, list) else project_list
            vol_24h = p.get("socialVolume24h") or 0
            vol_7d  = p.get("socialVolume7d") or 0
            avg_7d  = vol_7d / 7 if vol_7d else 0
            change  = ((vol_24h - avg_7d) / avg_7d * 100) if avg_7d else 0
            raw_sent = p.get("sentiment") or 0
            sentiment_pct = round((raw_sent + 1) / 2 * 100)

            results.append({
                "slug": slug,
                "name": p.get("name", slug),
                "symbol": p.get("ticker", slug.upper()),
                "social_volume_24h": round(vol_24h),
                "sentiment": sentiment_pct,
                "change_pct": round(change, 1),
            })

    results.sort(key=lambda x: x["social_volume_24h"], reverse=True)
    return {"data": results}

# ── 트렌딩 (Santiment) ─────────────────────────────────────────
@app.get("/api/trending")
async def get_trending():
    if not SAN_KEY:
        return {"error": "SANTIMENT_API_KEY not set"}

    query = """
    {
      getTrendingWords(from: "utc_now-1d", to: "utc_now", interval: "1d", size: 10) {
        datetime
        topWords { word score }
      }
    }
    """
    headers = {"Authorization": f"Apikey {SAN_KEY}"}
    async with httpx.AsyncClient() as client:
        r = await client.post(SANTIMENT_URL, json={"query": query}, headers=headers, timeout=15)
        return r.json()

# ── Reddit 핫 포스트 (인증 없이 JSON API) ──────────────────────
@app.get("/api/reddit")
async def get_reddit():
    headers = {
        "User-Agent": "finance-dashboard/1.0 (by /u/anonymous)"
    }
    all_posts = []

    async with httpx.AsyncClient() as client:
        for sub in SUBREDDITS:
            try:
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
                r = await client.get(url, headers=headers, timeout=10, follow_redirects=True)
                if r.status_code != 200:
                    continue
                data = r.json()
                posts = data.get("data", {}).get("children", [])
                for p in posts:
                    d = p.get("data", {})
                    if d.get("stickied"):
                        continue
                    all_posts.append({
                        "subreddit": d.get("subreddit_name_prefixed", f"r/{sub}"),
                        "title": d.get("title", ""),
                        "score": d.get("score", 0),
                        "comments": d.get("num_comments", 0),
                        "url": f"https://reddit.com{d.get('permalink', '')}",
                        "category": "crypto" if sub in ["CryptoCurrency", "Bitcoin", "ethereum"] else "finance",
                    })
            except Exception:
                continue

    # 점수 기준 정렬
    all_posts.sort(key=lambda x: x["score"], reverse=True)
    return {"data": all_posts[:20]}

# ── 헬스체크 ───────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "cc_key": "set" if CC_KEY else "missing",
        "san_key": "set" if SAN_KEY else "missing",
        "reddit": "no-auth-required",
    }
