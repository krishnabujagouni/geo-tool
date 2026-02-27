"""
GEO Tool API - FastAPI Backend

Endpoints:
- POST /api/analyze - Combined SEO + GEO analysis
- POST /api/analyze/seo - SEO only
- POST /api/analyze/geo - GEO only
- POST /api/generate/faq - AI-generate FAQ section
- POST /api/rewrite - AI-rewrite content for GEO
- POST /api/analyze-issues - AI-analyze issues with specific fixes
- POST /api/generate/schema/article - Generate Article schema
- POST /api/generate/schema/howto - Generate HowTo schema
"""
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict

from app.core.scraper import scrape_url, get_metadata
from app.scoring.scorer import calculate_geo_score
from app.scoring.seo_scorer import calculate_seo_score
from app.scoring.combined_scorer import calculate_combined_score
from app.services.ai_service import (
    is_ai_enabled,
    get_ai_provider,
    generate_faq,
    rewrite_content,
    analyze_issues,
    generate_article_schema,
    generate_howto_schema
)
from app.services.visibility_checker import check_ai_visibility
from app.services.article_generator import generate_article, generate_article_outline
from app.services.ssr_checker import check_ssr

# Create app
app = FastAPI(
    title="GEO Tool API",
    description="SEO + GEO - Optimize for Google AND AI search engines",
    version="2.0.0"
)

# CORS - allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== REQUEST/RESPONSE MODELS ==============

class AnalyzeRequest(BaseModel):
    url: HttpUrl

class FAQRequest(BaseModel):
    content: str
    num_questions: int = 5

class FAQResponse(BaseModel):
    faqs: List[Dict]
    schema_markup: str
    html: str
    ai_generated: bool
    error: Optional[str] = None

class RewriteRequest(BaseModel):
    content: str
    improvements: List[str]
    issues: Optional[List[Dict]] = None

class RewriteResponse(BaseModel):
    original: str
    rewritten: Optional[str]
    changes: List[Dict]
    predicted_score_increase: int
    error: Optional[str] = None

class AnalyzeIssuesRequest(BaseModel):
    content: str
    issues: List[Dict]

class ArticleSchemaRequest(BaseModel):
    title: str
    description: str
    author: str = "Unknown"
    date_published: Optional[str] = None
    url: Optional[str] = None

class HowToSchemaRequest(BaseModel):
    title: str
    description: str
    steps: List[str]

class SchemaResponse(BaseModel):
    schema_markup: str


# ============== ENDPOINTS ==============

@app.get("/")
async def root():
    """API info and health check"""
    return {
        "name": "GEO Tool API",
        "version": "2.0.0",
        "description": "SEO + GEO Combined Analysis",
        "ai_enabled": is_ai_enabled(),
        "endpoints": {
            "POST /api/analyze": "Combined SEO + GEO analysis",
            "POST /api/analyze/seo": "SEO only analysis",
            "POST /api/analyze/geo": "GEO only analysis",
            "POST /api/generate/faq": "AI-generate FAQ section",
            "POST /api/rewrite": "AI-rewrite content",
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "ai_enabled": is_ai_enabled(),
        "ai_provider": get_ai_provider()
    }


@app.post("/api/analyze")
async def analyze_combined(request: AnalyzeRequest):
    """
    Combined SEO + GEO analysis
    
    Returns:
        - Combined score (0-100)
        - SEO score with breakdown
        - GEO score with breakdown
        - Unified issues and recommendations
    """
    url = str(request.url)
    
    try:
        content, html = await scrape_url(url)
        
        if not content or len(content.strip()) < 100:
            raise HTTPException(400, "Could not extract meaningful content")
        
        metadata = get_metadata(html)
        result = await calculate_combined_score(url, content, html)
        result["metadata"] = metadata
        
        return result
        
    except httpx.TimeoutException:
        raise HTTPException(504, "Request timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, f"Failed to fetch: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")


@app.post("/api/analyze/seo")
async def analyze_seo_only(request: AnalyzeRequest):
    """SEO only analysis"""
    url = str(request.url)
    
    try:
        content, html = await scrape_url(url)
        
        if not content or len(content.strip()) < 100:
            raise HTTPException(400, "Could not extract meaningful content")
        
        metadata = get_metadata(html)
        result = calculate_seo_score(url, content, html)
        result["url"] = url
        result["metadata"] = metadata
        result["grade"] = get_grade(result["score"])
        
        return result
        
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")


@app.post("/api/analyze/geo")
async def analyze_geo_only(request: AnalyzeRequest):
    """GEO only analysis"""
    url = str(request.url)
    
    try:
        content, html = await scrape_url(url)
        
        if not content or len(content.strip()) < 100:
            raise HTTPException(400, "Could not extract meaningful content")
        
        metadata = get_metadata(html)
        result = await calculate_geo_score(url, content, html)
        result["metadata"] = metadata
        
        return result
        
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")


def get_grade(score: int) -> str:
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B"
    if score >= 60: return "C"
    if score >= 50: return "D"
    return "F"


@app.post("/api/generate/faq", response_model=FAQResponse)
async def generate_faq_endpoint(request: FAQRequest):
    """AI-generate FAQ section from content"""
    if not is_ai_enabled():
        raise HTTPException(400, "AI features require ANTHROPIC_API_KEY in .env")
    
    result = await generate_faq(request.content, request.num_questions)
    
    return {
        "faqs": result.get("faqs", []),
        "schema_markup": result.get("schema", ""),
        "html": result.get("html", ""),
        "ai_generated": result.get("ai_generated", False),
        "error": result.get("error")
    }


@app.post("/api/rewrite", response_model=RewriteResponse)
async def rewrite_content_endpoint(request: RewriteRequest):
    """AI-rewrite content to improve SEO + GEO"""
    if not is_ai_enabled():
        raise HTTPException(400, "AI features require ANTHROPIC_API_KEY in .env")
    
    result = await rewrite_content(
        request.content,
        request.improvements,
        request.issues
    )
    
    return result


@app.post("/api/analyze-issues")
async def analyze_issues_endpoint(request: AnalyzeIssuesRequest):
    """AI-analyze detected issues and provide specific fix recommendations"""
    if not is_ai_enabled():
        raise HTTPException(400, "AI features require ANTHROPIC_API_KEY in .env")
    
    result = await analyze_issues(request.content, request.issues)
    return result


@app.post("/api/generate/schema/article", response_model=SchemaResponse)
async def generate_article_schema_endpoint(request: ArticleSchemaRequest):
    """Generate Article JSON-LD schema"""
    schema = generate_article_schema(
        title=request.title,
        description=request.description,
        author=request.author,
        date_published=request.date_published,
        url=request.url
    )
    return {"schema_markup": schema}


@app.post("/api/generate/schema/howto", response_model=SchemaResponse)
async def generate_howto_schema_endpoint(request: HowToSchemaRequest):
    """Generate HowTo JSON-LD schema"""
    schema = generate_howto_schema(
        title=request.title,
        description=request.description,
        steps=request.steps
    )
    return {"schema_markup": schema}


@app.post("/api/visibility")
async def check_visibility_endpoint(request: AnalyzeRequest):
    """
    Check AI visibility for a website
    
    Checks:
    - robots.txt (AI crawler permissions)
    - sitemap.xml (page discovery)
    - llms.txt (AI-friendly description)
    
    Returns status, recommendations, and file templates
    """
    url = str(request.url)
    
    try:
        result = await check_ai_visibility(url)
        return result
    except Exception as e:
        raise HTTPException(500, f"Error checking visibility: {str(e)}")


class ArticleRequest(BaseModel):
    keywords: List[str]
    instructions: Optional[str] = None
    example_content: Optional[str] = None
    word_count: int = 1500


@app.post("/api/generate/article")
async def generate_article_endpoint(request: ArticleRequest):
    """
    Generate a full SEO + GEO optimized article
    
    Args:
        keywords: List of target keywords (1-5)
        instructions: Optional custom instructions
        example_content: Optional example article for style
        word_count: Target word count (default 1500)
    
    Returns:
        - title
        - meta_description
        - article (markdown)
        - faq
        - schema markup
    """
    if not is_ai_enabled():
        raise HTTPException(400, "AI features require ANTHROPIC_API_KEY in .env")
    
    if not request.keywords or len(request.keywords) == 0:
        raise HTTPException(400, "At least one keyword is required")
    
    if len(request.keywords) > 5:
        raise HTTPException(400, "Maximum 5 keywords allowed")
    
    try:
        result = await generate_article(
            keywords=request.keywords,
            instructions=request.instructions,
            example_content=request.example_content,
            word_count=request.word_count
        )
        
        if result.get("error"):
            raise HTTPException(500, result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(500, f"Error generating article: {str(e)}")


@app.post("/api/generate/article/outline")
async def generate_outline_endpoint(request: ArticleRequest):
    """Generate article outline only (faster preview)"""
    if not is_ai_enabled():
        raise HTTPException(400, "AI features require ANTHROPIC_API_KEY in .env")
    
    try:
        result = await generate_article_outline(request.keywords)
        return result
    except Exception as e:
        raise HTTPException(500, f"Error generating outline: {str(e)}")


@app.post("/api/ssr-check")
async def check_ssr_endpoint(request: AnalyzeRequest):
    """
    Check if a website is server-side rendered
    
    Returns:
        - is_ssr: bool
        - render_type: SSR | CSR | Hybrid | Static
        - score (0-100)
        - detailed checks
        - recommendations
    """
    url = str(request.url)
    
    try:
        result = await check_ssr(url)
        return result
    except Exception as e:
        raise HTTPException(500, f"Error checking SSR: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
