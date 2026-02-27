"""
GEO Scorer - Unified scoring module

Combines all scoring categories:
- Citeability (25 pts): Statistics, citations, quotes
- Structure (20 pts): Headers, FAQ, answer blocks
- Authority (20 pts): Author, E-E-A-T, dates
- Extractability (15 pts): Readability, clarity
- Technical (20 pts): AI crawlers, SSR, schema
"""
import re
import httpx
from typing import Dict, List, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

from app.scoring.patterns import (
    STAT_PATTERNS, QUOTE_PATTERNS, DEFINITION_PATTERNS,
    SUMMARY_SIGNALS, CREDIBLE_DOMAINS, AI_BOTS
)
from app.config import settings


async def calculate_geo_score(url: str, content: str, html: str) -> Dict:
    """Calculate complete GEO score (0-100)"""
    
    soup = BeautifulSoup(html, 'lxml') if html else None
    
    # Calculate all category scores
    citeability = score_citeability(content)
    structure = score_structure(content, html, soup)
    authority = score_authority(content, html, soup, url)
    extractability = score_extractability(content, html, soup)
    technical = await score_technical(url, html, soup)
    
    # Combine scores
    total = (citeability["score"] + structure["score"] + authority["score"] + 
             extractability["score"] + technical["score"])
    
    # Apply penalties
    word_count = len(content.split())
    if word_count < 300:
        total = int(total * 0.7)
    elif word_count < 500:
        total = int(total * 0.85)
    
    total = max(0, min(100, total))
    
    # Collect issues
    all_issues = []
    for cat in [citeability, structure, authority, extractability, technical]:
        all_issues.extend(cat.get("issues", []))
    
    # Sort by impact
    impact_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_issues.sort(key=lambda x: impact_order.get(x.get("impact", "low"), 4))
    
    return {
        "url": url,
        "score": total,
        "grade": get_grade(total),
        "breakdown": {
            "citeability": format_category(citeability),
            "structure": format_category(structure),
            "authority": format_category(authority),
            "extractability": format_category(extractability),
            "technical": format_category(technical)
        },
        "issues": all_issues[:10],
        "quick_wins": generate_quick_wins(all_issues, technical),
        "word_count": word_count
    }


def format_category(cat: Dict) -> Dict:
    """Format category for response"""
    ratio = cat["score"] / cat["max"] if cat["max"] > 0 else 0
    if ratio >= 0.8:
        label = "Excellent"
    elif ratio >= 0.6:
        label = "Good"
    elif ratio >= 0.4:
        label = "Needs Work"
    else:
        label = "Poor"
    
    return {
        "score": cat["score"],
        "max": cat["max"],
        "label": label
    }


def get_grade(score: int) -> str:
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B"
    if score >= 60: return "C"
    if score >= 50: return "D"
    return "F"


def generate_quick_wins(issues: List, technical: Dict) -> List[str]:
    """Generate quick win recommendations"""
    wins = []
    
    # Check technical for schema
    if technical.get("breakdown", {}).get("schema", 0) < 2:
        wins.append("Add FAQ schema markup (+2 points)")
    
    for issue in issues[:5]:
        if issue.get("impact") in ["high", "critical"]:
            fix = issue.get("fix", "")
            impact = issue.get("predicted_impact", "")
            if fix:
                wins.append(f"{fix} ({impact})" if impact else fix)
    
    return wins[:5]


# ============== CITEABILITY (25 pts) ==============

def score_citeability(content: str) -> Dict:
    """Score citeability: stats, citations, quotes (max 25)"""
    word_count = len(content.split())
    if word_count == 0:
        return {"score": 0, "max": 25, "issues": []}
    
    issues = []
    score = 0
    
    # Statistics (0-8)
    stats_count = sum(len(re.findall(p, content, re.I)) for p in STAT_PATTERNS)
    stats_per_500 = (stats_count / word_count) * 500
    
    if stats_per_500 >= 5: score += 8
    elif stats_per_500 >= 3: score += 6
    elif stats_per_500 >= 1: score += 4
    elif stats_per_500 >= 0.5: score += 2
    else:
        issues.append({
            "category": "citeability", "issue": "Low statistics density",
            "impact": "high", "current": f"{stats_per_500:.1f} per 500 words",
            "target": "3+ per 500 words", "fix": "Add 5-7 statistics with sources",
            "predicted_impact": "+4-6 points"
        })
    
    # Citations (0-7)
    url_pattern = r'https?://(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+)'
    urls = re.findall(url_pattern, content)
    credible = 0
    for url in urls:
        for tier, domains in CREDIBLE_DOMAINS.items():
            if any(d in url.lower() for d in domains):
                credible += 2 if tier == 'tier_1' else 1
                break
    
    if credible >= 10: score += 7
    elif credible >= 6: score += 5
    elif credible >= 3: score += 3
    elif credible >= 1: score += 2
    else:
        issues.append({
            "category": "citeability", "issue": "No credible source citations",
            "impact": "high", "fix": "Add citations to .gov, .edu, or research sources",
            "predicted_impact": "+3-5 points"
        })
    
    # Quotes (0-5)
    quotes = sum(len(re.findall(p, content, re.I)) for p in QUOTE_PATTERNS)
    if quotes >= 3: score += 5
    elif quotes >= 2: score += 4
    elif quotes >= 1: score += 2
    else:
        issues.append({
            "category": "citeability", "issue": "No expert quotes found",
            "impact": "medium", "fix": "Add 2-3 quotes from industry experts",
            "predicted_impact": "+2-4 points"
        })
    
    # Tables/charts (0-3)
    has_tables = bool(re.search(r'<table|\\|.*\\|.*\\|', content, re.I))
    if has_tables: score += 3
    
    # Original research (0-2)
    research = any(re.search(p, content, re.I) for p in 
                   [r'our (study|research|survey)', r'we (surveyed|analyzed)'])
    if research: score += 2
    
    return {"score": min(score, 25), "max": 25, "issues": issues}


# ============== STRUCTURE (20 pts) ==============

def score_structure(content: str, html: str, soup: BeautifulSoup) -> Dict:
    """Score structure: headers, FAQ, blocks (max 20)"""
    issues = []
    score = 0
    
    if not soup:
        return {"score": 0, "max": 20, "issues": []}
    
    # Headers (0-5)
    h1s = soup.find_all('h1')
    h2s = soup.find_all('h2')
    h3s = soup.find_all('h3')
    
    if len(h1s) == 1 and len(h2s) >= 2:
        score += 5
    elif len(h1s) == 1:
        score += 3
    elif len(h2s) >= 2:
        score += 2
    else:
        issues.append({
            "category": "structure", "issue": "Weak header hierarchy",
            "impact": "medium", "fix": "Add clear H2 section headers",
            "predicted_impact": "+2-3 points"
        })
    
    # Answer blocks (0-5)
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    if paragraphs:
        answer_blocks = sum(1 for p in paragraphs if 30 <= len(p.split()) <= 80)
        ratio = answer_blocks / len(paragraphs)
        if ratio >= 0.5: score += 5
        elif ratio >= 0.3: score += 3
        else:
            issues.append({
                "category": "structure", "issue": "Few answer-ready blocks",
                "impact": "medium", "fix": "Create 40-60 word paragraphs",
                "predicted_impact": "+2-3 points"
            })
    
    # Summary (0-3)
    first_500 = content[:500].lower()
    has_summary = any(re.search(p, first_500, re.I) for p in SUMMARY_SIGNALS)
    if has_summary: score += 3
    else:
        issues.append({
            "category": "structure", "issue": "No TL;DR or summary",
            "impact": "medium", "fix": "Add Key Takeaways at the top",
            "predicted_impact": "+2-3 points"
        })
    
    # FAQ (0-4)
    has_faq = bool(soup.find(['h2', 'h3'], string=re.compile(r'faq|frequently', re.I)))
    has_faq_schema = 'FAQPage' in html
    if has_faq_schema: score += 4
    elif has_faq: score += 2
    else:
        issues.append({
            "category": "structure", "issue": "No FAQ section",
            "impact": "medium", "fix": "Add FAQ with 3-5 questions",
            "predicted_impact": "+2-4 points"
        })
    
    # Lists (0-3)
    lists = soup.find_all(['ul', 'ol'])
    if len(lists) >= 2: score += 3
    elif len(lists) >= 1: score += 2
    
    return {"score": min(score, 20), "max": 20, "issues": issues}


# ============== AUTHORITY (20 pts) ==============

def score_authority(content: str, html: str, soup: BeautifulSoup, url: str) -> Dict:
    """Score authority: author, E-E-A-T, dates (max 20)"""
    issues = []
    score = 0
    
    if not soup:
        return {"score": 0, "max": 20, "issues": []}
    
    # Author (0-5)
    has_author = bool(re.search(r'"author"|class=["\'][^"\']*author', html, re.I))
    if has_author: score += 5
    else:
        issues.append({
            "category": "authority", "issue": "No author attribution",
            "impact": "high", "fix": "Add author name and bio",
            "predicted_impact": "+3-5 points"
        })
    
    # Date (0-4)
    has_date = bool(re.search(r'datePublished|article:published_time|<time', html, re.I))
    if has_date: score += 4
    else:
        issues.append({
            "category": "authority", "issue": "No publish date",
            "impact": "medium", "fix": "Add datePublished schema",
            "predicted_impact": "+2-3 points"
        })
    
    # Organization (0-4)
    has_org = bool(re.search(r'"Organization"|/about|/contact', html, re.I))
    if has_org: score += 4
    
    # E-E-A-T signals (0-4)
    eeat = 0
    if re.search(r'(PhD|MD|MBA|certified|licensed)', content, re.I): eeat += 1
    if re.search(r'(years of experience|expert in)', content, re.I): eeat += 1
    if re.search(r'(award|featured in|recognized)', content, re.I): eeat += 1
    if re.search(r'(privacy.?policy|terms)', html, re.I): eeat += 1
    score += min(eeat, 4)
    
    # HTTPS (0-3)
    if url.startswith('https://'): score += 3
    else:
        issues.append({
            "category": "authority", "issue": "Not using HTTPS",
            "impact": "high", "fix": "Enable HTTPS",
            "predicted_impact": "+3 points"
        })
    
    return {"score": min(score, 20), "max": 20, "issues": issues}


# ============== EXTRACTABILITY (15 pts) ==============

def score_extractability(content: str, html: str, soup: BeautifulSoup) -> Dict:
    """Score extractability: readability, clarity (max 15)"""
    issues = []
    score = 0
    
    # Readability (0-5)
    if HAS_TEXTSTAT and len(content.split()) >= 100:
        try:
            fk = textstat.flesch_kincaid_grade(content)
            if fk <= 8: score += 5
            elif fk <= 10: score += 4
            elif fk <= 12: score += 3
            else:
                issues.append({
                    "category": "extractability", "issue": f"Content too complex (Grade {fk:.0f})",
                    "impact": "medium", "fix": "Simplify language, shorter sentences",
                    "predicted_impact": "+2-3 points"
                })
        except:
            score += 3
    else:
        score += 3
    
    # Entity clarity (0-3)
    word_count = len(content.split())
    if word_count > 0:
        ambiguous = len(re.findall(r'\b(this|that|it|they)\b', content, re.I))
        per_500 = (ambiguous / word_count) * 500
        if per_500 <= 10: score += 3
        elif per_500 <= 20: score += 2
    
    # Definitions (0-3)
    defs = sum(1 for p in DEFINITION_PATTERNS if re.search(p, content, re.I))
    if defs >= 2: score += 3
    elif defs >= 1: score += 2
    else:
        issues.append({
            "category": "extractability", "issue": "No clear definitions",
            "impact": "low", "fix": "Add 'X is defined as...' patterns",
            "predicted_impact": "+1-2 points"
        })
    
    # Semantic HTML (0-2)
    if soup and soup.find(['article', 'main', 'section']):
        score += 2
    
    # Schema (0-2)
    if 'application/ld+json' in html:
        score += 2
    
    return {"score": min(score, 15), "max": 15, "issues": issues}


# ============== TECHNICAL (20 pts) ==============

async def score_technical(url: str, html: str, soup: BeautifulSoup) -> Dict:
    """Score technical: AI crawlers, SSR, schema (max 20)"""
    issues = []
    score = 0
    breakdown = {}
    
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # AI Crawler Access (0-5)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{base_url}/robots.txt", timeout=5)
            if resp.status_code == 200:
                robots = resp.text.lower()
                blocked = sum(1 for bot in AI_BOTS if bot.lower() in robots and 'disallow' in robots)
                if blocked == 0: 
                    score += 5
                    breakdown["ai_crawlers"] = 5
                elif blocked <= 2:
                    score += 3
                    breakdown["ai_crawlers"] = 3
                else:
                    issues.append({
                        "category": "technical", "issue": f"{blocked} AI crawlers blocked",
                        "impact": "critical", "fix": "Allow GPTBot, ClaudeBot in robots.txt",
                        "predicted_impact": "+3-4 points"
                    })
                    breakdown["ai_crawlers"] = 1
            else:
                score += 5  # No robots.txt = all allowed
                breakdown["ai_crawlers"] = 5
    except:
        score += 4
        breakdown["ai_crawlers"] = 4
    
    # SSR (0-4)
    ssr_signals = [len(html) > 5000, '<article' in html.lower(), 
                   html.lower().count('<p') > 3]
    csr_signals = ['<div id="root"></div>' in html, 'Loading...' in html]
    
    if sum(ssr_signals) >= 2 and not any(csr_signals):
        score += 4
        breakdown["ssr"] = 4
    elif any(csr_signals):
        issues.append({
            "category": "technical", "issue": "Client-side rendered only",
            "impact": "high", "fix": "Implement SSR or static generation",
            "predicted_impact": "+3 points"
        })
        breakdown["ssr"] = 1
    else:
        score += 2
        breakdown["ssr"] = 2
    
    # Sitemap (0-3)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{base_url}/sitemap.xml", timeout=5)
            if resp.status_code == 200:
                score += 3
                breakdown["sitemap"] = 3
            else:
                issues.append({
                    "category": "technical", "issue": "No sitemap.xml",
                    "impact": "medium", "fix": "Create sitemap.xml",
                    "predicted_impact": "+2 points"
                })
                breakdown["sitemap"] = 0
    except:
        breakdown["sitemap"] = 1
    
    # Schema (0-4)
    schemas = set()
    if '"FAQPage"' in html: schemas.add("FAQ")
    if '"Article"' in html or '"BlogPosting"' in html: schemas.add("Article")
    if '"HowTo"' in html: schemas.add("HowTo")
    
    if "FAQ" in schemas: 
        score += 2
        breakdown["schema"] = 2
    else:
        issues.append({
            "category": "technical", "issue": "Missing FAQ schema",
            "impact": "medium", "fix": "Add FAQPage schema",
            "predicted_impact": "+2 points"
        })
        breakdown["schema"] = 0
    
    if schemas:
        score += 2
    
    # HTTPS (0-2)
    if url.startswith('https://'):
        score += 2
        breakdown["https"] = 2
    else:
        breakdown["https"] = 0
    
    # Speed (0-2)
    if len(html) < 200000:
        score += 2
        breakdown["speed"] = 2
    else:
        breakdown["speed"] = 1
    
    return {"score": min(score, 20), "max": 20, "issues": issues, "breakdown": breakdown}
