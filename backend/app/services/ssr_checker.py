"""
SSR Checker - Check if a website is Server-Side Rendered

Checks for:
- Content in initial HTML (vs client-side rendered)
- Meta tags present in HTML
- JavaScript framework indicators
- Hydration markers
- Content length analysis
"""
import re
import httpx
from typing import Dict, List
from bs4 import BeautifulSoup


async def check_ssr(url: str) -> Dict:
    """
    Check if a website is server-side rendered
    
    Returns:
        {
            "url": str,
            "is_ssr": bool,
            "render_type": "SSR" | "CSR" | "Static" | "Hybrid",
            "score": int (0-100),
            "checks": {
                "content_in_html": {...},
                "meta_tags": {...},
                "framework_detection": {...},
                "js_indicators": {...}
            },
            "issues": [...],
            "recommendations": [...]
        }
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; GEOBot/1.0)",
                    "Accept": "text/html"
                },
                follow_redirects=True,
                timeout=15
            )
            
            if response.status_code != 200:
                return {
                    "url": url,
                    "error": f"HTTP {response.status_code}",
                    "is_ssr": None
                }
            
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "is_ssr": None
        }
    
    # Run all checks
    content_check = check_content_in_html(html, soup)
    meta_check = check_meta_tags(soup)
    framework_check = detect_framework(html, soup)
    js_check = check_js_indicators(html, soup)
    heading_check = check_headings(soup)
    
    # Calculate score
    score = 0
    score += content_check["score"]  # 0-30
    score += meta_check["score"]      # 0-25
    score += heading_check["score"]   # 0-20
    score += js_check["score"]        # 0-15
    score += 10 if framework_check["is_ssr_framework"] else 0  # 0-10
    
    # Determine render type
    if score >= 80:
        render_type = "SSR"
        is_ssr = True
    elif score >= 60:
        render_type = "Hybrid"
        is_ssr = True
    elif score >= 40:
        render_type = "Partial CSR"
        is_ssr = False
    else:
        render_type = "CSR"
        is_ssr = False
    
    # Collect issues
    issues = []
    if content_check["score"] < 20:
        issues.append({
            "severity": "critical",
            "issue": "Very little content in initial HTML",
            "detail": f"Only {content_check['content_length']} characters of content found"
        })
    if not meta_check["has_title"]:
        issues.append({
            "severity": "high",
            "issue": "Missing title tag",
            "detail": "Title tag not found in HTML"
        })
    if not meta_check["has_description"]:
        issues.append({
            "severity": "high",
            "issue": "Missing meta description",
            "detail": "Meta description not found in HTML"
        })
    if not heading_check["has_h1"]:
        issues.append({
            "severity": "medium",
            "issue": "Missing H1 tag",
            "detail": "No H1 heading found in initial HTML"
        })
    if js_check["has_empty_root"]:
        issues.append({
            "severity": "critical",
            "issue": "Empty root div detected",
            "detail": "Found empty container (likely CSR app)"
        })
    if js_check["has_loading_indicator"]:
        issues.append({
            "severity": "medium",
            "issue": "Loading indicator found",
            "detail": "Page may show loading state to crawlers"
        })
    
    # Generate recommendations
    recommendations = generate_ssr_recommendations(
        content_check, meta_check, framework_check, js_check, heading_check
    )
    
    return {
        "url": url,
        "is_ssr": is_ssr,
        "render_type": render_type,
        "score": min(score, 100),
        "grade": get_grade(score),
        "checks": {
            "content_in_html": content_check,
            "meta_tags": meta_check,
            "headings": heading_check,
            "framework": framework_check,
            "js_indicators": js_check
        },
        "issues": issues,
        "recommendations": recommendations
    }


def check_content_in_html(html: str, soup: BeautifulSoup) -> Dict:
    """Check if meaningful content is in the initial HTML"""
    
    # Remove scripts and styles
    for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'header']):
        tag.decompose()
    
    # Get text content
    body = soup.find('body')
    if body:
        text = body.get_text(separator=' ', strip=True)
    else:
        text = soup.get_text(separator=' ', strip=True)
    
    content_length = len(text)
    word_count = len(text.split())
    
    # Count paragraphs with actual content
    paragraphs = soup.find_all('p')
    content_paragraphs = [p for p in paragraphs if len(p.get_text(strip=True)) > 50]
    
    # Score based on content
    score = 0
    if content_length > 5000:
        score = 30
    elif content_length > 2000:
        score = 25
    elif content_length > 1000:
        score = 20
    elif content_length > 500:
        score = 15
    elif content_length > 200:
        score = 10
    else:
        score = 5
    
    return {
        "content_length": content_length,
        "word_count": word_count,
        "paragraph_count": len(content_paragraphs),
        "has_substantial_content": content_length > 1000,
        "score": score
    }


def check_meta_tags(soup: BeautifulSoup) -> Dict:
    """Check for essential meta tags"""
    
    title = soup.find('title')
    has_title = title is not None and len(title.get_text(strip=True)) > 0
    title_text = title.get_text(strip=True) if title else None
    title_length = len(title_text) if title_text else 0
    
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    has_description = meta_desc is not None and meta_desc.get('content')
    desc_text = meta_desc.get('content') if meta_desc else None
    desc_length = len(desc_text) if desc_text else 0
    
    # Open Graph tags
    og_title = soup.find('meta', property='og:title')
    og_desc = soup.find('meta', property='og:description')
    og_image = soup.find('meta', property='og:image')
    has_og = og_title is not None
    
    # Twitter cards
    twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
    has_twitter = twitter_card is not None
    
    # Canonical
    canonical = soup.find('link', rel='canonical')
    has_canonical = canonical is not None
    
    # Score
    score = 0
    if has_title and 30 <= title_length <= 60:
        score += 8
    elif has_title:
        score += 5
    
    if has_description and 120 <= desc_length <= 160:
        score += 8
    elif has_description:
        score += 5
    
    if has_og:
        score += 5
    if has_canonical:
        score += 4
    
    return {
        "has_title": has_title,
        "title_text": title_text,
        "title_length": title_length,
        "has_description": has_description,
        "description_text": desc_text[:100] + "..." if desc_text and len(desc_text) > 100 else desc_text,
        "description_length": desc_length,
        "has_og_tags": has_og,
        "has_twitter_card": has_twitter,
        "has_canonical": has_canonical,
        "score": score
    }


def check_headings(soup: BeautifulSoup) -> Dict:
    """Check heading structure"""
    
    h1s = soup.find_all('h1')
    h2s = soup.find_all('h2')
    h3s = soup.find_all('h3')
    
    has_h1 = len(h1s) > 0
    h1_count = len(h1s)
    h1_text = h1s[0].get_text(strip=True) if h1s else None
    
    score = 0
    if h1_count == 1:
        score += 10
    elif h1_count > 1:
        score += 5  # Multiple H1s is not ideal
    
    if len(h2s) >= 2:
        score += 7
    elif len(h2s) >= 1:
        score += 4
    
    if len(h3s) >= 1:
        score += 3
    
    return {
        "has_h1": has_h1,
        "h1_count": h1_count,
        "h1_text": h1_text,
        "h2_count": len(h2s),
        "h3_count": len(h3s),
        "proper_hierarchy": h1_count == 1 and len(h2s) >= 2,
        "score": score
    }


def detect_framework(html: str, soup: BeautifulSoup) -> Dict:
    """Detect JavaScript framework and SSR capability"""
    
    framework = None
    is_ssr_framework = False
    indicators = []
    
    # Next.js
    if '__NEXT_DATA__' in html or 'next/dist' in html or '_next/' in html:
        framework = "Next.js"
        is_ssr_framework = True
        indicators.append("Next.js detected (SSR capable)")
    
    # Nuxt.js
    elif '__NUXT__' in html or 'nuxt' in html.lower():
        framework = "Nuxt.js"
        is_ssr_framework = True
        indicators.append("Nuxt.js detected (SSR capable)")
    
    # Gatsby
    elif '___gatsby' in html or 'gatsby' in html.lower():
        framework = "Gatsby"
        is_ssr_framework = True
        indicators.append("Gatsby detected (Static/SSR)")
    
    # Astro
    elif 'astro' in html.lower():
        framework = "Astro"
        is_ssr_framework = True
        indicators.append("Astro detected (SSR by default)")
    
    # SvelteKit
    elif '__sveltekit' in html or 'svelte' in html.lower():
        framework = "SvelteKit"
        is_ssr_framework = True
        indicators.append("SvelteKit detected (SSR capable)")
    
    # React (CSR)
    elif 'react' in html.lower() or soup.find(id='root') or soup.find(id='app'):
        root_div = soup.find(id='root') or soup.find(id='app')
        if root_div and len(root_div.get_text(strip=True)) < 50:
            framework = "React (CSR)"
            is_ssr_framework = False
            indicators.append("React detected (Client-Side Rendered)")
        else:
            framework = "React"
            is_ssr_framework = True
            indicators.append("React with SSR or content")
    
    # Vue (CSR)
    elif 'vue' in html.lower():
        framework = "Vue.js"
        is_ssr_framework = False
        indicators.append("Vue.js detected")
    
    # Angular
    elif 'ng-version' in html or 'angular' in html.lower():
        framework = "Angular"
        is_ssr_framework = False
        indicators.append("Angular detected")
    
    # WordPress
    elif 'wp-content' in html or 'wordpress' in html.lower():
        framework = "WordPress"
        is_ssr_framework = True
        indicators.append("WordPress detected (Server rendered)")
    
    return {
        "framework": framework,
        "is_ssr_framework": is_ssr_framework,
        "indicators": indicators
    }


def check_js_indicators(html: str, soup: BeautifulSoup) -> Dict:
    """Check for CSR indicators"""
    
    # Empty root/app div
    root_div = soup.find(id='root') or soup.find(id='app') or soup.find(id='__next')
    has_empty_root = False
    if root_div:
        root_content = root_div.get_text(strip=True)
        has_empty_root = len(root_content) < 50
    
    # Loading indicators
    loading_patterns = ['loading...', 'loading…', 'please wait', 'spinner', 'skeleton']
    has_loading = any(p in html.lower() for p in loading_patterns)
    
    # Noscript fallback
    noscript = soup.find('noscript')
    has_noscript = noscript is not None
    noscript_message = noscript.get_text(strip=True)[:100] if noscript else None
    
    # Heavy JS bundles
    scripts = soup.find_all('script', src=True)
    large_bundles = [s for s in scripts if 'bundle' in str(s.get('src', '')).lower() or 'chunk' in str(s.get('src', '')).lower()]
    
    # Score (higher is better - means less CSR indicators)
    score = 15
    if has_empty_root:
        score -= 10
    if has_loading:
        score -= 3
    if not has_noscript and has_empty_root:
        score -= 2
    
    return {
        "has_empty_root": has_empty_root,
        "has_loading_indicator": has_loading,
        "has_noscript_fallback": has_noscript,
        "noscript_message": noscript_message,
        "script_count": len(scripts),
        "has_large_bundles": len(large_bundles) > 0,
        "score": max(score, 0)
    }


def generate_ssr_recommendations(content, meta, framework, js, headings) -> List[Dict]:
    """Generate recommendations based on checks"""
    
    recommendations = []
    
    if js["has_empty_root"]:
        recommendations.append({
            "priority": 1,
            "title": "Enable Server-Side Rendering",
            "description": "Your page appears to be client-side rendered. Search engines and AI may not see your content.",
            "action": "Implement SSR using Next.js, Nuxt.js, or Astro",
            "impact": "Critical for SEO and AI visibility"
        })
    
    if content["content_length"] < 500:
        recommendations.append({
            "priority": 1,
            "title": "Add Content to Initial HTML",
            "description": f"Only {content['content_length']} characters found in initial HTML.",
            "action": "Ensure critical content is server-rendered, not loaded via JavaScript",
            "impact": "Search engines see your actual content"
        })
    
    if not meta["has_title"]:
        recommendations.append({
            "priority": 2,
            "title": "Add Title Tag",
            "description": "No title tag found in HTML response.",
            "action": "Add a unique, descriptive title tag",
            "impact": "Essential for SEO and AI understanding"
        })
    
    if not meta["has_description"]:
        recommendations.append({
            "priority": 2,
            "title": "Add Meta Description",
            "description": "No meta description found.",
            "action": "Add a compelling meta description (120-160 characters)",
            "impact": "Improves click-through rates"
        })
    
    if not headings["has_h1"]:
        recommendations.append({
            "priority": 3,
            "title": "Add H1 Heading",
            "description": "No H1 tag found in initial HTML.",
            "action": "Add one H1 tag with your main keyword",
            "impact": "Helps search engines understand page topic"
        })
    
    if not meta["has_og_tags"]:
        recommendations.append({
            "priority": 3,
            "title": "Add Open Graph Tags",
            "description": "No Open Graph tags found.",
            "action": "Add og:title, og:description, og:image tags",
            "impact": "Better social media sharing previews"
        })
    
    if not js["has_noscript_fallback"] and js["has_empty_root"]:
        recommendations.append({
            "priority": 3,
            "title": "Add Noscript Fallback",
            "description": "No fallback content for JavaScript-disabled browsers.",
            "action": "Add <noscript> with basic content or message",
            "impact": "Accessibility and crawler support"
        })
    
    return recommendations


def get_grade(score: int) -> str:
    """Convert score to grade"""
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B"
    if score >= 60: return "C"
    if score >= 50: return "D"
    return "F"
