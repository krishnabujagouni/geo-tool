"""
Combined Scorer - SEO + GEO unified scoring

Provides:
- SEO Score (0-100): Traditional Google SEO
- GEO Score (0-100): AI Search Engine Optimization
- Combined Score (0-100): Weighted average
- Unified recommendations
"""
from typing import Dict, List
from app.scoring.scorer import calculate_geo_score
from app.scoring.seo_scorer import calculate_seo_score


async def calculate_combined_score(url: str, content: str, html: str) -> Dict:
    """
    Calculate combined SEO + GEO score
    
    Returns:
        {
            "url": str,
            "combined_score": int (0-100),
            "combined_grade": str,
            "seo": { full SEO results },
            "geo": { full GEO results },
            "unified_issues": [...],
            "unified_quick_wins": [...],
            "recommendations": [...]
        }
    """
    
    # Calculate both scores
    geo_result = await calculate_geo_score(url, content, html)
    seo_result = calculate_seo_score(url, content, html)
    
    # Combined score (weighted: 50% SEO, 50% GEO)
    combined_score = int((seo_result["score"] * 0.5) + (geo_result["score"] * 0.5))
    
    # Merge and deduplicate issues
    all_issues = []
    seen_issues = set()
    
    for issue in seo_result.get("issues", []):
        issue["source"] = "seo"
        key = issue.get("issue", "")
        if key not in seen_issues:
            all_issues.append(issue)
            seen_issues.add(key)
    
    for issue in geo_result.get("issues", []):
        issue["source"] = "geo"
        key = issue.get("issue", "")
        if key not in seen_issues:
            all_issues.append(issue)
            seen_issues.add(key)
    
    # Sort by impact
    impact_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_issues.sort(key=lambda x: impact_order.get(x.get("impact", "low"), 4))
    
    # Merge quick wins
    all_quick_wins = []
    seen_wins = set()
    
    for win in seo_result.get("quick_wins", []) + geo_result.get("quick_wins", []):
        if win not in seen_wins:
            all_quick_wins.append(win)
            seen_wins.add(win)
    
    # Generate unified recommendations
    recommendations = generate_unified_recommendations(seo_result, geo_result, all_issues)
    
    return {
        "url": url,
        "combined_score": combined_score,
        "combined_grade": get_grade(combined_score),
        "seo": {
            "score": seo_result["score"],
            "grade": get_grade(seo_result["score"]),
            "breakdown": seo_result["breakdown"],
            "issues": seo_result.get("issues", [])[:5]
        },
        "geo": {
            "score": geo_result["score"],
            "grade": get_grade(geo_result["score"]),
            "breakdown": geo_result["breakdown"],
            "issues": geo_result.get("issues", [])[:5]
        },
        "unified_issues": all_issues[:10],
        "unified_quick_wins": all_quick_wins[:5],
        "recommendations": recommendations,
        "word_count": geo_result.get("word_count", 0)
    }


def get_grade(score: int) -> str:
    """Convert score to letter grade"""
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B"
    if score >= 60: return "C"
    if score >= 50: return "D"
    return "F"


def generate_unified_recommendations(seo: Dict, geo: Dict, issues: List) -> List[Dict]:
    """Generate prioritized recommendations that improve both SEO and GEO"""
    
    recommendations = []
    
    # Check for issues that affect both
    seo_score = seo["score"]
    geo_score = geo["score"]
    
    # Priority 1: Critical issues
    if seo_score < 50 and geo_score < 50:
        recommendations.append({
            "priority": 1,
            "title": "Critical: Major improvements needed",
            "description": "Both SEO and GEO scores are below 50. Focus on foundational fixes first.",
            "actions": [
                "Add meta title and description",
                "Add H1 and H2 headers",
                "Increase content length to 1000+ words",
                "Add statistics and citations"
            ],
            "impact": "Could improve combined score by 20-30 points"
        })
    
    # Check meta tags
    seo_meta = seo.get("breakdown", {}).get("meta_tags", {})
    if seo_meta.get("score", 0) < seo_meta.get("max", 20) * 0.6:
        recommendations.append({
            "priority": 2,
            "title": "Fix Meta Tags",
            "description": "Meta tags affect both Google rankings and how AI understands your page.",
            "actions": [
                "Write compelling title (30-60 chars)",
                "Write meta description (120-160 chars)",
                "Include primary keyword in both"
            ],
            "impact": "Improves SEO by 10-15 points"
        })
    
    # Check content/citeability
    geo_cite = geo.get("breakdown", {}).get("citeability", {})
    if geo_cite.get("score", 0) < geo_cite.get("max", 25) * 0.5:
        recommendations.append({
            "priority": 2,
            "title": "Add Statistics & Citations",
            "description": "AI engines prefer content with data and credible sources.",
            "actions": [
                "Add 3-5 relevant statistics",
                "Cite sources (.gov, .edu, research papers)",
                "Include expert quotes"
            ],
            "impact": "Improves GEO by 10-15 points, also helps E-E-A-T for SEO"
        })
    
    # Check structure
    geo_structure = geo.get("breakdown", {}).get("structure", {})
    seo_structure = seo.get("breakdown", {}).get("structure", {})
    
    if (geo_structure.get("score", 0) < geo_structure.get("max", 20) * 0.5 or 
        seo_structure.get("score", 0) < seo_structure.get("max", 20) * 0.5):
        recommendations.append({
            "priority": 3,
            "title": "Improve Content Structure",
            "description": "Good structure helps both Google crawlers and AI extraction.",
            "actions": [
                "Use one H1 tag for main title",
                "Add H2 subheadings every 200-300 words",
                "Add FAQ section with schema",
                "Use bullet lists for key points"
            ],
            "impact": "Improves both SEO and GEO by 5-10 points each"
        })
    
    # Check technical
    if seo.get("breakdown", {}).get("technical", {}).get("score", 0) < 15:
        recommendations.append({
            "priority": 3,
            "title": "Fix Technical Issues",
            "description": "Technical issues hurt both traditional and AI search visibility.",
            "actions": [
                "Enable HTTPS",
                "Add canonical tag",
                "Add viewport meta for mobile",
                "Ensure clean URL structure"
            ],
            "impact": "Foundation for good rankings in both"
        })
    
    # Add FAQ recommendation if missing
    has_faq_issue = any("FAQ" in str(issue) for issue in issues)
    if has_faq_issue:
        recommendations.append({
            "priority": 4,
            "title": "Add FAQ Section",
            "description": "FAQs are highly extractable by AI and can appear as rich results in Google.",
            "actions": [
                "Add 3-5 common questions",
                "Keep answers concise (40-60 words)",
                "Add FAQPage schema markup"
            ],
            "impact": "Major boost to GEO, potential rich results in Google"
        })
    
    # Sort by priority
    recommendations.sort(key=lambda x: x.get("priority", 99))
    
    return recommendations[:5]
