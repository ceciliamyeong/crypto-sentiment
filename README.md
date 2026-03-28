# 🚀 크립토 소셜 센티먼트 대시보드 — Vercel 배포 가이드

## 📁 폴더 구조
```
dashboard-vercel/
├── api/
│   └── index.py       ← FastAPI 서버 (Vercel Serverless)
├── static/
│   └── index.html     ← 대시보드 화면
├── vercel.json        ← Vercel 라우팅 설정
├── requirements.txt   ← 패키지 목록
└── .gitignore         ← .env 보호
```

---

## 🛠 배포 순서

### 1단계 — GitHub에 올리기
1. GitHub에서 새 레포 만들기 (예: `crypto-dashboard`)
2. 이 폴더 전체를 레포에 업로드
   - `.env` 파일은 올리지 마세요! (.gitignore에 포함됨)

### 2단계 — Vercel 연결
1. https://vercel.com 접속 → 구글/깃허브로 가입
2. **"Add New Project"** 클릭
3. GitHub 레포 선택 (`crypto-dashboard`)
4. **"Deploy"** 클릭 (설정 건드릴 필요 없음)

### 3단계 — 환경변수 설정 (API 키)
배포 후 Vercel 대시보드에서:
1. 프로젝트 클릭 → **Settings** → **Environment Variables**
2. 아래 두 개 추가:

| Name | Value |
|------|-------|
| `CRYPTOCOMPARE_API_KEY` | 크립토컴페어 키 |
| `LUNARCRUSH_API_KEY` | 루나크러쉬 키 |

3. **Save** 후 → **Deployments** → **Redeploy** 클릭

### 4단계 — 접속
```
https://[프로젝트명].vercel.app
```

---

## ✅ 키 정상 확인
배포 후 아래 URL로 키 설정 확인 가능:
```
https://[프로젝트명].vercel.app/api/health
```
→ `{"status":"ok","cc_key":"set","lc_key":"set"}` 뜨면 성공!

---

## 🔄 이후 업데이트
GitHub에 푸시하면 Vercel이 자동으로 재배포해줘요.
