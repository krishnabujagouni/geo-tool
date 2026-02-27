"""
AI Visibility Checker

Checks if a website has the essential files for AI search visibility:
1. robots.txt - Permissions for AI crawlers
2. sitemap.xml - Page discovery
3. llms.txt - AI-friendly site description

Also generates templates for missing files.
"""
import httpx
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
from datetime import datetime


# AI Crawlers to check
AI_CRAWLERS = [
    {"name": "GPTBot", "owner": "OpenAI (ChatGPT)"},
    {"name": "ChatGPT-User", "owner": "OpenAI (ChatGPT)"},
    {"name": "Google-Extended", "owner": "Google (Gemini/AI Overview)"},
    {"name": "anthropic-ai", "owner": "Anthropic (Claude)"},
    {"name": "Claude-Web", "owner": "Anthropic (Claude)"},
    {"name": "PerplexityBot", "owner": "Perplexity"},
    {"name": "Amazonbot", "owner": "Amazon (Alexa)"},
    {"name": "Bytespider", "owner": "ByteDance (TikTok)"},
]


async def check_ai_visibility(url: str) -> Dict:
    """
    Check if a website is visible to AI search engines
    
    Returns:
        {
            "url": str,
            "overall_score": int (0-100),
            "overall_status": "visible" | "partial" | "blocked",
            "robots_txt": { status, details, crawlers },
            "sitemap_xml": { status, details, urls_count },
            "llms_txt": { status, details },
            "recommendations": [...],
            "templates": { robots_txt, sitemap_xml, llms_txt }
        }
    """
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    domain = parsed.netloc.replace("www.", "")
    
    # Check all three files
    robots_result = await check_robots_txt(base_url)
    sitemap_result = await check_sitemap_xml(base_url)
    llms_result = await check_llms_txt(base_url)
    
    # Calculate overall score
    score = 0
    if robots_result["status"] == "found" and robots_result["ai_allowed"]:
        score += 40
    elif robots_result["status"] == "found":
        score += 20
    elif robots_result["status"] == "not_found":
        score += 30  # No robots.txt = all allowed
    
    if sitemap_result["status"] == "found":
        score += 35
    
    if llms_result["status"] == "found":
        score += 25
    
    # Determine overall status
    if score >= 80:
        overall_status = "visible"
    elif score >= 40:
        overall_status = "partial"
    else:
        overall_status = "blocked"
    
    # Generate recommendations
    recommendations = generate_recommendations(robots_result, sitemap_result, llms_result)
    
    # Generate templates
    templates = generate_templates(domain, base_url)
    
    return {
        "url": base_url,
        "overall_score": score,
        "overall_status": overall_status,
        "robots_txt": robots_result,
        "sitemap_xml": sitemap_result,
        "llms_txt": llms_result,
        "recommendations": recommendations,
        "templates": templates
    }


async def check_robots_txt(base_url: str) -> Dict:
    """Check robots.txt for AI crawler permissions"""
    result = {
        "status": "not_found",
        "url": f"{base_url}/robots.txt",
        "ai_allowed": True,  # Default: if no robots.txt, all allowed
        "crawlers": [],
        "details": ""
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/robots.txt", timeout=10)
            
            if response.status_code == 200:
                content = response.text.lower()
                result["status"] = "found"
                result["content"] = response.text[:2000]  # First 2000 chars
                
                # Check each AI crawler
                for crawler in AI_CRAWLERS:
                    crawler_status = check_crawler_permission(response.text, crawler["name"])
                    result["crawlers"].append({
                        "name": crawler["name"],
                        "owner": crawler["owner"],
                        "status": crawler_status
                    })
                
                # Count blocked crawlers
                blocked = [c for c in result["crawlers"] if c["status"] == "blocked"]
                allowed = [c for c in result["crawlers"] if c["status"] == "allowed"]
                
                if len(blocked) == 0:
                    result["ai_allowed"] = True
                    result["details"] = f"All {len(AI_CRAWLERS)} AI crawlers allowed"
                elif len(blocked) == len(AI_CRAWLERS):
                    result["ai_allowed"] = False
                    result["details"] = "All AI crawlers are blocked!"
                else:
                    result["ai_allowed"] = True  # Partial
                    result["details"] = f"{len(allowed)} allowed, {len(blocked)} blocked"
                    
            elif response.status_code == 404:
                result["status"] = "not_found"
                result["details"] = "No robots.txt found (all crawlers allowed by default)"
                result["ai_allowed"] = True
            else:
                result["status"] = "error"
                result["details"] = f"HTTP {response.status_code}"
                
    except Exception as e:
        result["status"] = "error"
        result["details"] = str(e)
    
    return result


def check_crawler_permission(robots_content: str, crawler_name: str) -> str:
    """Check if a specific crawler is allowed or blocked"""
    lines = robots_content.split('\n')
    current_agent = None
    crawler_lower = crawler_name.lower()
    
    # Check for specific rules for this crawler
    for line in lines:
        line = line.strip().lower()
        
        if line.startswith('user-agent:'):
            agent = line.split(':', 1)[1].strip()
            if agent == '*' or crawler_lower in agent:
                current_agent = agent
        
        elif current_agent and line.startswith('disallow:'):
            path = line.split(':', 1)[1].strip()
            if path == '/' or path == '/*':
                return "blocked"
        
        elif current_agent and line.startswith('allow:'):
            path = line.split(':', 1)[1].strip()
            if path == '/' or path == '/*':
                return "allowed"
    
    return "allowed"  # Default: allowed if not explicitly blocked


async def check_sitemap_xml(base_url: str) -> Dict:
    """Check for sitemap.xml"""
    result = {
        "status": "not_found",
        "url": f"{base_url}/sitemap.xml",
        "urls_count": 0,
        "details": ""
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/sitemap.xml", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check if valid XML sitemap
                if '<urlset' in content or '<sitemapindex' in content:
                    result["status"] = "found"
                    
                    # Count URLs
                    urls = re.findall(r'<loc>(.*?)</loc>', content)
                    result["urls_count"] = len(urls)
                    result["details"] = f"Found {len(urls)} URLs in sitemap"
                    result["sample_urls"] = urls[:5]  # First 5 URLs
                else:
                    result["status"] = "invalid"
                    result["details"] = "File exists but not valid XML sitemap"
                    
            elif response.status_code == 404:
                result["status"] = "not_found"
                result["details"] = "No sitemap.xml found"
            else:
                result["status"] = "error"
                result["details"] = f"HTTP {response.status_code}"
                
    except Exception as e:
        result["status"] = "error"
        result["details"] = str(e)
    
    return result


async def check_llms_txt(base_url: str) -> Dict:
    """Check for llms.txt (AI-friendly site description)"""
    result = {
        "status": "not_found",
        "url": f"{base_url}/llms.txt",
        "details": ""
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/llms.txt", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                result["status"] = "found"
                result["content"] = content[:2000]
                result["details"] = f"Found llms.txt ({len(content)} chars)"
                
                # Check for key sections
                has_description = bool(re.search(r'description|about|what we do', content, re.I))
                has_features = bool(re.search(r'features|services|products', content, re.I))
                has_contact = bool(re.search(r'contact|email|support', content, re.I))
                
                result["has_sections"] = {
                    "description": has_description,
                    "features": has_features,
                    "contact": has_contact
                }
                
            elif response.status_code == 404:
                result["status"] = "not_found"
                result["details"] = "No llms.txt found (recommended for AI visibility)"
            else:
                result["status"] = "error"
                result["details"] = f"HTTP {response.status_code}"
                
    except Exception as e:
        result["status"] = "error"
        result["details"] = str(e)
    
    return result


def generate_recommendations(robots: Dict, sitemap: Dict, llms: Dict) -> List[Dict]:
    """Generate actionable recommendations"""
    recommendations = []
    
    # Robots.txt recommendations
    if robots["status"] == "not_found":
        recommendations.append({
            "priority": 2,
            "file": "robots.txt",
            "issue": "No robots.txt file found",
            "action": "Create robots.txt to explicitly allow AI crawlers",
            "impact": "Ensures AI bots know they're welcome"
        })
    elif not robots.get("ai_allowed", True):
        recommendations.append({
            "priority": 1,
            "file": "robots.txt",
            "issue": "AI crawlers are blocked",
            "action": "Update robots.txt to allow GPTBot, Claude-Web, etc.",
            "impact": "Critical - unblocks AI from indexing your content"
        })
    
    # Sitemap recommendations
    if sitemap["status"] == "not_found":
        recommendations.append({
            "priority": 1,
            "file": "sitemap.xml",
            "issue": "No sitemap.xml found",
            "action": "Create sitemap.xml with all your page URLs",
            "impact": "Helps AI discover all your content"
        })
    elif sitemap["status"] == "invalid":
        recommendations.append({
            "priority": 1,
            "file": "sitemap.xml",
            "issue": "Sitemap is not valid XML",
            "action": "Fix sitemap XML format",
            "impact": "Current sitemap can't be read by crawlers"
        })
    
    # llms.txt recommendations
    if llms["status"] == "not_found":
        recommendations.append({
            "priority": 2,
            "file": "llms.txt",
            "issue": "No llms.txt found",
            "action": "Create llms.txt to help AI understand your site",
            "impact": "AI assistants will better understand and recommend your site"
        })
    
    # Sort by priority
    recommendations.sort(key=lambda x: x["priority"])
    
    return recommendations


def generate_templates(domain: str, base_url: str) -> Dict:
    """Generate template files for the user"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    robots_template = f"""# Allow all search engines and AI crawlers
User-agent: *
Allow: /

# Explicitly allow AI crawlers
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: PerplexityBot
Allow: /

# Sitemap location
Sitemap: {base_url}/sitemap.xml

# Block sensitive paths (customize as needed)
Disallow: /admin/
Disallow: /private/
Disallow: /api/
"""

    sitemap_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Homepage -->
  <url>
    <loc>{base_url}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  
  <!-- About Page -->
  <url>
    <loc>{base_url}/about</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  
  <!-- Add your pages here -->
  <url>
    <loc>{base_url}/your-page</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>
"""

    llms_template = f"""# llms.txt - AI-Readable Site Information

# Site Information
> Site Name: {domain}
> URL: {base_url}
> Description: [Add a brief description of your site/business]

# What We Do
[Describe your product/service in 2-3 sentences. What problem do you solve?]

# Main Features/Services
- Feature 1: [Description]
- Feature 2: [Description]
- Feature 3: [Description]

# Key Pages
- Homepage: {base_url}/
- About: {base_url}/about
- Blog: {base_url}/blog
- Contact: {base_url}/contact

# Target Audience
[Describe who your ideal customer/user is]

# Contact
- Email: contact@{domain}
- Support: {base_url}/support

# Last Updated: {today}
"""

    return {
        "robots_txt": robots_template,
        "sitemap_xml": sitemap_template,
        "llms_txt": llms_template
    }
