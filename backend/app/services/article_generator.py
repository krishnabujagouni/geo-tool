"""
AI Article Generator - Generate SEO + GEO optimized articles

Features:
- Generates 1500-2000 word articles
- Optimized for both Google SEO and AI search engines
- Includes proper structure (H1, H2, H3)
- Adds statistics, citations, FAQ section
- Includes schema markup suggestions
"""
import re
import json
from typing import Dict, List, Optional
from app.config import settings
from app.services.ai_service import call_llm, is_ai_enabled


async def generate_article(
    keywords: List[str],
    instructions: Optional[str] = None,
    example_content: Optional[str] = None,
    word_count: int = 1500
) -> Dict:
    """
    Generate a full SEO + GEO optimized article
    
    Args:
        keywords: List of target keywords (1-5)
        instructions: Optional custom instructions (tone, style, audience)
        example_content: Optional example article for style matching
        word_count: Target word count (default 1500)
    
    Returns:
        {
            "title": str,
            "meta_description": str,
            "article": str (markdown),
            "faq": [{"question": str, "answer": str}],
            "schema": str (JSON-LD),
            "keywords_used": [str],
            "word_count": int,
            "geo_optimizations": [str]
        }
    """
    if not is_ai_enabled():
        return {
            "error": "AI features require ANTHROPIC_API_KEY in .env",
            "article": None
        }
    
    primary_keyword = keywords[0] if keywords else "topic"
    all_keywords = ", ".join(keywords)
    
    # Build the prompt
    prompt = f"""You are an expert SEO and GEO (Generative Engine Optimization) content writer. 
Generate a comprehensive, high-quality article optimized for both Google Search AND AI search engines (ChatGPT, Perplexity, Claude).

TARGET KEYWORDS: {all_keywords}
PRIMARY KEYWORD: {primary_keyword}
TARGET WORD COUNT: {word_count} words

{f'CUSTOM INSTRUCTIONS: {instructions}' if instructions else ''}

{f'STYLE REFERENCE (match this tone/style): {example_content[:1000]}' if example_content else ''}

ARTICLE REQUIREMENTS:

1. SEO OPTIMIZATION:
   - Include primary keyword in title, first paragraph, and H2 headings
   - Use semantic variations of keywords naturally
   - Write compelling meta description (150-160 chars)
   - Use proper heading hierarchy (H1 > H2 > H3)
   - Keep paragraphs short (2-4 sentences)
   - Include internal linking suggestions [LINK: topic]

2. GEO OPTIMIZATION (for AI search engines):
   - Add 3-5 statistics with sources (use realistic data)
   - Include 2-3 expert quotes (can be attributed to "[Expert Name], [Title]")
   - Create answer-ready blocks (40-60 words that directly answer questions)
   - Use clear definitions: "X is defined as..."
   - Add a FAQ section with 5 questions
   - Make content easily extractable and quotable

3. STRUCTURE:
   - Compelling H1 title with primary keyword
   - TL;DR or Key Takeaways at the top
   - 4-6 H2 sections with descriptive headings
   - H3 subsections where appropriate
   - Bullet points for lists
   - FAQ section at the end
   - Strong conclusion with call-to-action

4. CONTENT QUALITY:
   - Actionable, practical advice
   - Current and accurate information
   - Engaging, conversational tone
   - No fluff or filler content

Return your response in this exact JSON format:
{{
    "title": "Your SEO-Optimized Title Here",
    "meta_description": "Compelling 150-160 character description with primary keyword",
    "article": "Full markdown article content here...",
    "faq": [
        {{"question": "Question 1?", "answer": "Answer 1"}},
        {{"question": "Question 2?", "answer": "Answer 2"}},
        {{"question": "Question 3?", "answer": "Answer 3"}},
        {{"question": "Question 4?", "answer": "Answer 4"}},
        {{"question": "Question 5?", "answer": "Answer 5"}}
    ],
    "keywords_used": ["keyword1", "keyword2"],
    "geo_optimizations": ["Added 4 statistics", "Included 2 expert quotes", "Created 5 answer blocks"]
}}

IMPORTANT: Return ONLY valid JSON. No markdown code blocks, no explanations outside the JSON."""

    try:
        response = call_llm(prompt, max_tokens=4000)
        response = response.strip()
        
        # Clean markdown if present
        if response.startswith("```"):
            response = re.sub(r'^```json?\n?', '', response)
            response = re.sub(r'\n?```$', '', response)
        
        result = json.loads(response)
        
        # Calculate actual word count
        article_text = result.get("article", "")
        actual_word_count = len(article_text.split())
        result["word_count"] = actual_word_count
        
        # Generate schema markup
        result["schema"] = generate_article_schema(
            title=result.get("title", ""),
            description=result.get("meta_description", ""),
            keywords=keywords
        )
        
        # Generate FAQ schema
        if result.get("faq"):
            result["faq_schema"] = generate_faq_schema(result["faq"])
        
        return result
        
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse AI response: {str(e)}",
            "raw_response": response[:500] if response else None,
            "article": None
        }
    except Exception as e:
        return {
            "error": str(e),
            "article": None
        }


def generate_article_schema(title: str, description: str, keywords: List[str]) -> str:
    """Generate Article JSON-LD schema"""
    from datetime import datetime
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title[:110],
        "description": description[:200],
        "keywords": ", ".join(keywords),
        "datePublished": datetime.now().strftime("%Y-%m-%d"),
        "dateModified": datetime.now().strftime("%Y-%m-%d"),
        "author": {
            "@type": "Person",
            "name": "[Your Name]"
        },
        "publisher": {
            "@type": "Organization",
            "name": "[Your Site Name]"
        }
    }
    
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


def generate_faq_schema(faqs: List[Dict]) -> str:
    """Generate FAQPage JSON-LD schema"""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["answer"]
                }
            }
            for faq in faqs
        ]
    }
    
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


async def generate_article_outline(keywords: List[str]) -> Dict:
    """
    Generate just an article outline (faster, for preview)
    """
    if not is_ai_enabled():
        return {"error": "AI features require ANTHROPIC_API_KEY"}
    
    prompt = f"""Create an article outline for these keywords: {', '.join(keywords)}

Return JSON format:
{{
    "title": "Suggested title",
    "sections": [
        {{"heading": "H2 heading", "subheadings": ["H3 sub 1", "H3 sub 2"], "key_points": ["point 1", "point 2"]}}
    ],
    "suggested_stats": ["Stat to include 1", "Stat to include 2"],
    "faq_ideas": ["Question 1?", "Question 2?", "Question 3?"]
}}

Return ONLY valid JSON."""

    try:
        response = call_llm(prompt, max_tokens=1000)
        response = response.strip()
        
        if response.startswith("```"):
            response = re.sub(r'^```json?\n?', '', response)
            response = re.sub(r'\n?```$', '', response)
        
        return json.loads(response)
    except Exception as e:
        return {"error": str(e)}
