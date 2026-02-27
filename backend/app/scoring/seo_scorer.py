"""
SEO Scorer - Traditional SEO scoring module

Scores content based on:
- Meta Tags (20 pts): Title, description
- Content Quality (20 pts): Word count, keywords, readability
- Structure (20 pts): Headers, links, images
- Technical (20 pts): URL, canonical, mobile
- Performance (20 pts): Page size, speed

Total: 100 points
"""
import re
from typing import Dict, List
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def calculate_seo_score(url: str, content: str, html: str) -> Dict:
    """Calculate SEO score (0-100)"""
    
    soup = BeautifulSoup(html, 'lxml') if html else None
    
    if not soup:
        return {"score": 0, "max": 100, "breakdown": {}, "issues": []}
    
    # Calculate all category scores
    meta = score_meta_tags(soup, url)
    content_quality = score_content_quality(content, soup)
    structure = score_structure_seo(soup, html)
    technical = score_technical_seo(soup, url, html)
    performance = score_performance(html)
    
    total = (
        meta["score"] +
        content_quality["score"] +
        structure["score"] +
        technical["score"] +
        performance["score"]
    )
    
    # Collect issues
    all_issues = []
    for cat in [meta, content_quality, structure, technical, performance]:
        all_issues.extend(cat.get("issues", []))
    
    impact_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_issues.sort(key=lambda x: impact_order.get(x.get("impact", "low"), 4))
    
    return {
        "score": min(total, 100),
        "max": 100,
        "breakdown": {
            "meta_tags": format_cat(meta),
            "content_quality": format_cat(content_quality),
            "structure": format_cat(structure),
            "technical": format_cat(technical),
            "performance": format_cat(performance)
        },
        "issues": all_issues[:10],
        "quick_wins": get_quick_wins(all_issues)
    }


def format_cat(cat: Dict) -> Dict:
    ratio = cat["score"] / cat["max"] if cat["max"] > 0 else 0
    if ratio >= 0.8: label = "Excellent"
    elif ratio >= 0.6: label = "Good"
    elif ratio >= 0.4: label = "Needs Work"
    else: label = "Poor"
    return {"score": cat["score"], "max": cat["max"], "label": label}


def get_quick_wins(issues: List) -> List[str]:
    wins = []
    for issue in issues[:5]:
        if issue.get("impact") in ["high", "critical"] and issue.get("fix"):
            wins.append(issue["fix"])
    return wins


# ============== META TAGS (20 pts) ==============

def score_meta_tags(soup: BeautifulSoup, url: str) -> Dict:
    """Score meta tags: title, description"""
    issues = []
    score = 0
    
    # Title tag (10 pts)
    title = soup.find('title')
    if title:
        title_text = title.get_text(strip=True)
        title_len = len(title_text)
        
        if 30 <= title_len <= 60:
            score += 10
        elif 20 <= title_len <= 70:
            score += 7
            issues.append({
                "category": "seo", "issue": f"Title length not optimal ({title_len} chars)",
                "impact": "medium", "fix": "Keep title between 30-60 characters",
                "predicted_impact": "+3 points"
            })
        else:
            score += 3
            issues.append({
                "category": "seo", "issue": f"Title too {'short' if title_len < 20 else 'long'} ({title_len} chars)",
                "impact": "high", "fix": "Rewrite title to 30-60 characters",
                "predicted_impact": "+7 points"
            })
    else:
        issues.append({
            "category": "seo", "issue": "Missing title tag",
            "impact": "critical", "fix": "Add a title tag",
            "predicted_impact": "+10 points"
        })
    
    # Meta description (10 pts)
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        desc_len = len(meta_desc['content'])
        
        if 120 <= desc_len <= 160:
            score += 10
        elif 80 <= desc_len <= 200:
            score += 6
            issues.append({
                "category": "seo", "issue": f"Meta description not optimal ({desc_len} chars)",
                "impact": "medium", "fix": "Keep meta description 120-160 characters",
                "predicted_impact": "+4 points"
            })
        else:
            score += 3
            issues.append({
                "category": "seo", "issue": f"Meta description too {'short' if desc_len < 80 else 'long'}",
                "impact": "high", "fix": "Rewrite to 120-160 characters",
                "predicted_impact": "+7 points"
            })
    else:
        issues.append({
            "category": "seo", "issue": "Missing meta description",
            "impact": "critical", "fix": "Add meta description tag",
            "predicted_impact": "+10 points"
        })
    
    return {"score": score, "max": 20, "issues": issues}


# ============== CONTENT QUALITY (20 pts) ==============

def score_content_quality(content: str, soup: BeautifulSoup) -> Dict:
    """Score content quality: word count, readability"""
    issues = []
    score = 0
    
    word_count = len(content.split())
    
    # Word count (10 pts)
    if word_count >= 1500:
        score += 10
    elif word_count >= 1000:
        score += 8
    elif word_count >= 500:
        score += 5
    elif word_count >= 300:
        score += 3
    else:
        issues.append({
            "category": "seo", "issue": f"Thin content ({word_count} words)",
            "impact": "high", "fix": "Add more content (aim for 1000+ words)",
            "predicted_impact": "+5-7 points"
        })
    
    # Paragraph structure (5 pts)
    paragraphs = soup.find_all('p')
    if len(paragraphs) >= 5:
        score += 5
    elif len(paragraphs) >= 3:
        score += 3
    else:
        issues.append({
            "category": "seo", "issue": "Few paragraphs found",
            "impact": "medium", "fix": "Break content into more paragraphs",
            "predicted_impact": "+2-3 points"
        })
    
    # Sentence length (5 pts)
    sentences = re.split(r'[.!?]+', content)
    if sentences:
        avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_words <= 20:
            score += 5
        elif avg_words <= 25:
            score += 3
        else:
            issues.append({
                "category": "seo", "issue": f"Sentences too long (avg {avg_words:.0f} words)",
                "impact": "low", "fix": "Shorten sentences for readability",
                "predicted_impact": "+2 points"
            })
    
    return {"score": score, "max": 20, "issues": issues}


# ============== STRUCTURE (20 pts) ==============

def score_structure_seo(soup: BeautifulSoup, html: str) -> Dict:
    """Score structure: headers, links, images"""
    issues = []
    score = 0
    
    # H1 tag (5 pts)
    h1s = soup.find_all('h1')
    if len(h1s) == 1:
        score += 5
    elif len(h1s) > 1:
        score += 2
        issues.append({
            "category": "seo", "issue": f"Multiple H1 tags ({len(h1s)} found)",
            "impact": "medium", "fix": "Use only one H1 tag per page",
            "predicted_impact": "+3 points"
        })
    else:
        issues.append({
            "category": "seo", "issue": "Missing H1 tag",
            "impact": "high", "fix": "Add one H1 tag with main keyword",
            "predicted_impact": "+5 points"
        })
    
    # Subheadings (5 pts)
    h2s = soup.find_all('h2')
    h3s = soup.find_all('h3')
    if len(h2s) >= 2:
        score += 5
    elif len(h2s) >= 1 or len(h3s) >= 2:
        score += 3
    else:
        issues.append({
            "category": "seo", "issue": "Few subheadings",
            "impact": "medium", "fix": "Add H2 subheadings to structure content",
            "predicted_impact": "+2-3 points"
        })
    
    # Internal links (5 pts)
    links = soup.find_all('a', href=True)
    internal_links = [l for l in links if not l['href'].startswith(('http', '//', 'mailto', 'tel'))]
    if len(internal_links) >= 3:
        score += 5
    elif len(internal_links) >= 1:
        score += 3
    else:
        issues.append({
            "category": "seo", "issue": "No internal links",
            "impact": "medium", "fix": "Add internal links to other pages",
            "predicted_impact": "+2-3 points"
        })
    
    # Image alt tags (5 pts)
    images = soup.find_all('img')
    if images:
        imgs_with_alt = [img for img in images if img.get('alt')]
        ratio = len(imgs_with_alt) / len(images)
        if ratio >= 0.9:
            score += 5
        elif ratio >= 0.5:
            score += 3
            issues.append({
                "category": "seo", "issue": f"Some images missing alt tags ({len(images) - len(imgs_with_alt)}/{len(images)})",
                "impact": "medium", "fix": "Add alt text to all images",
                "predicted_impact": "+2 points"
            })
        else:
            issues.append({
                "category": "seo", "issue": "Most images missing alt tags",
                "impact": "high", "fix": "Add descriptive alt text to images",
                "predicted_impact": "+3-5 points"
            })
    else:
        score += 3  # No images is okay
    
    return {"score": score, "max": 20, "issues": issues}


# ============== TECHNICAL SEO (20 pts) ==============

def score_technical_seo(soup: BeautifulSoup, url: str, html: str) -> Dict:
    """Score technical SEO: URL, canonical, mobile"""
    issues = []
    score = 0
    
    parsed = urlparse(url)
    
    # HTTPS (5 pts)
    if parsed.scheme == 'https':
        score += 5
    else:
        issues.append({
            "category": "seo", "issue": "Not using HTTPS",
            "impact": "critical", "fix": "Enable SSL/HTTPS",
            "predicted_impact": "+5 points"
        })
    
    # URL structure (5 pts)
    path = parsed.path
    if len(path) < 75 and '-' in path and not re.search(r'[A-Z]', path):
        score += 5
    elif len(path) < 100:
        score += 3
    else:
        issues.append({
            "category": "seo", "issue": "URL too long or poorly structured",
            "impact": "low", "fix": "Use short, hyphenated, lowercase URLs",
            "predicted_impact": "+2 points"
        })
    
    # Canonical tag (5 pts)
    canonical = soup.find('link', rel='canonical')
    if canonical and canonical.get('href'):
        score += 5
    else:
        issues.append({
            "category": "seo", "issue": "Missing canonical tag",
            "impact": "medium", "fix": "Add canonical tag to prevent duplicate content",
            "predicted_impact": "+5 points"
        })
    
    # Viewport/mobile (5 pts)
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport:
        score += 5
    else:
        issues.append({
            "category": "seo", "issue": "Missing viewport meta tag",
            "impact": "high", "fix": "Add viewport meta tag for mobile",
            "predicted_impact": "+5 points"
        })
    
    return {"score": score, "max": 20, "issues": issues}


# ============== PERFORMANCE (20 pts) ==============

def score_performance(html: str) -> Dict:
    """Score performance indicators"""
    issues = []
    score = 0
    
    html_size = len(html)
    
    # HTML size (10 pts)
    if html_size < 100000:  # < 100KB
        score += 10
    elif html_size < 200000:  # < 200KB
        score += 7
    elif html_size < 500000:  # < 500KB
        score += 4
        issues.append({
            "category": "seo", "issue": f"Large HTML size ({html_size // 1000}KB)",
            "impact": "medium", "fix": "Reduce HTML size, remove inline CSS/JS",
            "predicted_impact": "+3 points"
        })
    else:
        issues.append({
            "category": "seo", "issue": f"Very large HTML ({html_size // 1000}KB)",
            "impact": "high", "fix": "Significantly reduce page size",
            "predicted_impact": "+6 points"
        })
    
    # Render-blocking resources (5 pts)
    soup = BeautifulSoup(html, 'lxml')
    scripts = soup.find_all('script', src=True)
    async_defer = [s for s in scripts if s.get('async') or s.get('defer')]
    
    if len(scripts) == 0 or len(async_defer) >= len(scripts) * 0.5:
        score += 5
    else:
        issues.append({
            "category": "seo", "issue": "Render-blocking scripts",
            "impact": "medium", "fix": "Add async or defer to script tags",
            "predicted_impact": "+3 points"
        })
    
    # Lazy loading (5 pts)
    if 'loading="lazy"' in html or 'loading=lazy' in html:
        score += 5
    else:
        score += 2  # Partial credit
        issues.append({
            "category": "seo", "issue": "No lazy loading for images",
            "impact": "low", "fix": "Add loading='lazy' to images",
            "predicted_impact": "+2 points"
        })
    
    return {"score": score, "max": 20, "issues": issues}
