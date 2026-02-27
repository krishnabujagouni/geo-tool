# 🎯 GEO Tool - Generative Engine Optimization

AI-powered tool to analyze and optimize your content for AI search engines (ChatGPT, Perplexity, Claude, Google AI).

![GEO Tool](https://via.placeholder.com/800x400?text=GEO+Tool+Screenshot)

## Features

### 📊 GEO Analyzer
- **GEO Score (0-100)**: Unified score across 5 categories
- **5 Scoring Categories**:
  - Citeability (25 pts): Statistics, citations, quotes
  - Structure (20 pts): Headers, FAQ, answer blocks
  - Authority (20 pts): Author, E-E-A-T, dates
  - Extractability (15 pts): Readability, clarity
  - Technical (20 pts): AI crawlers, SSR, schema
- **Issue Detection**: Prioritized list with specific fixes
- **Quick Wins**: Low-effort, high-impact improvements

### ✍️ AI Content Rewriter
- Add statistics with one click
- Add credible citations
- Add expert quotes
- Simplify language
- Create answer blocks (40-60 words)
- Add definitions
- **Powered by Claude AI**

### ❓ AI FAQ Generator
- Generate smart Q&As from content
- Creates questions real users would ask
- Outputs JSON-LD schema markup
- Outputs HTML with microdata
- **Powered by Claude AI**

## Tech Stack

- **Backend**: Python, FastAPI, Claude API
- **Frontend**: React, Next.js 14, Tailwind CSS
- **AI**: Anthropic Claude API

## Quick Start

### 1. Clone & Setup

```bash
git clone <repo>
cd geo-tool
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Start dev server
npm run dev
```

### 4. Open in Browser

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze` | POST | Analyze URL for GEO score |
| `/api/generate/faq` | POST | AI-generate FAQ section |
| `/api/rewrite` | POST | AI-rewrite content for GEO |
| `/api/analyze-issues` | POST | AI-analyze issues with fixes |
| `/api/generate/schema/article` | POST | Generate Article schema |
| `/api/generate/schema/howto` | POST | Generate HowTo schema |

## Example: Analyze URL

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

Response:
```json
{
  "url": "https://example.com/article",
  "score": 72,
  "grade": "B",
  "breakdown": {
    "citeability": {"score": 18, "max": 25, "label": "Good"},
    "structure": {"score": 15, "max": 20, "label": "Good"},
    "authority": {"score": 14, "max": 20, "label": "Needs Work"},
    "extractability": {"score": 12, "max": 15, "label": "Good"},
    "technical": {"score": 13, "max": 20, "label": "Good"}
  },
  "issues": [...],
  "quick_wins": [...]
}
```

## Project Structure

```
geo-tool/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Settings
│   │   ├── core/
│   │   │   └── scraper.py    # URL scraping
│   │   ├── scoring/
│   │   │   ├── scorer.py     # Main GEO scoring
│   │   │   └── patterns.py   # Regex patterns
│   │   └── services/
│   │       └── ai_service.py # Claude AI integration
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx      # Analyzer page
│   │   │   ├── rewriter/     # Rewriter page
│   │   │   └── faq/          # FAQ generator page
│   │   ├── components/
│   │   │   ├── ScoreCard.tsx
│   │   │   ├── CategoryBreakdown.tsx
│   │   │   ├── IssuesList.tsx
│   │   │   ├── QuickWins.tsx
│   │   │   ├── FAQGenerator.tsx
│   │   │   └── ContentRewriter.tsx
│   │   └── lib/
│   │       ├── api.ts        # API client
│   │       └── utils.ts      # Utilities
│   ├── package.json
│   └── .env.example
│
└── README.md
```

## Environment Variables

### Backend (.env)
```
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Required for AI features
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## AI Features Require API Key

The following features require `ANTHROPIC_API_KEY`:
- ✍️ AI Content Rewriter
- ❓ AI FAQ Generator
- 🔍 AI Issue Analyzer

The GEO Analyzer works without an API key (uses rule-based scoring).

## Scoring Methodology

Based on [Princeton GEO Research](https://arxiv.org/abs/2311.09735):

| Method | Impact |
|--------|--------|
| Add Statistics | +30-40% visibility |
| Add Citations | +30-40% visibility |
| Add Quotations | +30-40% visibility |
| Improve Fluency | +15-30% visibility |

## Roadmap

- [ ] Citation tracking across LLMs
- [ ] Prompt research tool
- [ ] Competitor benchmarking
- [ ] Weekly reports
- [ ] Chrome extension

## License

MIT
