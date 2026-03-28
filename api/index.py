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

COINS = [
    {"slug": "bitcoin",      "symbol": "BTC"},
    {"slug": "ethereum",     "symbol": "ETH"},
    {"slug": "solana",       "symbol": "SOL"},
    {"slug": "binance-coin", "symbol": "BNB"},
    {"slug": "xrp",          "symbol": "XRP"},
    {"slug": "dogecoin",     "symbol": "DOGE"},
    {"slug": "cardano",      "symbol": "ADA"},
    {"slug": "avalanche",    "symbol": "AVAX"},
    {"slug": "chainlink",    "symbol": "LINK"},
    {"slug": "polkadot",     "symbol": "DOT"},
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

    slugs = [c["slug"] for c in COINS]
    slugs_gql = str(slugs).replace("'", '"')

    query = """
    {
      allProjects(slugs: %s) {
        slug
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
        socialDominance: aggregatedTimeseriesData(
          metric: "social_dominance_total"
          from: "utc_now-1d"
          to: "utc_now"
          aggregation: AVG
        )
      }
    }
    """ % slugs_gql

    headers = {"Authorization": f"Apikey {SAN_KEY}"}
    async with httpx.AsyncClient() as client:
        r = await client.post(
            SANTIMENT_URL,
            json={"query": query},
            headers=headers,
            timeout=15
        )
        data = r.json()

    if "errors" in data:
        return {"error": data["errors"]}

    projects = data.get("data", {}).get("allProjects", [])

    result = []
    for p in projects:
        vol_24h = p.get("socialVolume24h") or 0
        vol_7d = p.get("socialVolume7d") or 0
        avg_7d = vol_7d / 7 if vol_7d else 0
        change = ((vol_24h - avg_7d) / avg_7d * 100) if avg_7d else 0
        raw_sent = p.get("sentiment") or 0
        sentiment_pct = round((raw_sent + 1) / 2 * 100)
        result.append({
            "slug": p.get("slug"),
            "name": p.get("name"),
            "symbol": p.get("ticker"),
            "social_volume_24h": round(vol_24h),
            "sentiment": sentiment_pct,
            "change_pct": round(change, 1),
            "social_dominance": round((p.get("socialDominance") or 0) * 100, 2),
        })

    result.sort(key=lambda x: x["social_volume_24h"], reverse=True)
    return {"data": result}

# ── 트렌딩 단어 (Santiment) ────────────────────────────────────
@app.get("/api/trending")
async def get_trending():
    if not SAN_KEY:
        return {"error": "SANTIMENT_API_KEY not set"}

    query = """
    {
      getTrendingWords(from: "utc_now-1d", to: "utc_now", interval: "1d", size: 10) {
        datetime
        topWords {
          word
          score
        }
      }
    }
    """
    headers = {"Authorization": f"Apikey {SAN_KEY}"}
    async with httpx.AsyncClient() as client:
        r = await client.post(
            SANTIMENT_URL,
            json={"query": query},
            headers=headers,
            timeout=15
        )
        return r.json()

# ── 헬스체크 ───────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "cc_key": "set" if CC_KEY else "missing",
        "san_key": "set" if SAN_KEY else "missing",
    }
