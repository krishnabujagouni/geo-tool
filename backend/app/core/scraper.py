"""
URL Scraper - Fetches and extracts content from URLs
"""
import httpx
import re
from bs4 import BeautifulSoup
from typing import Tuple, Dict
from app.config import settings


async def scrape_url(url: str) -> Tuple[str, str]:
    """
    Scrape URL and return (plain_text, raw_html)
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={
                "User-Agent": settings.user_agent,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.5",
            },
            follow_redirects=True,
            timeout=settings.request_timeout
        )
        response.raise_for_status()
    
    html = response.text
    text = extract_text(html)
    
    return text, html


def extract_text(html: str) -> str:
    """Extract readable text from HTML"""
    soup = BeautifulSoup(html, 'lxml')
    
    # Remove unwanted elements
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
        tag.decompose()
    
    # Find main content
    main = soup.find('main') or soup.find('article') or soup.find('body')
    
    if main:
        text = main.get_text(separator='\n', strip=True)
    else:
        text = soup.get_text(separator='\n', strip=True)
    
    # Clean up
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text


def get_metadata(html: str) -> Dict:
    """Extract page metadata"""
    soup = BeautifulSoup(html, 'lxml')
    
    title = soup.find('title')
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    
    return {
        "title": title.get_text(strip=True) if title else None,
        "description": meta_desc.get('content') if meta_desc else None,
        "word_count": len(extract_text(html).split())
    }
