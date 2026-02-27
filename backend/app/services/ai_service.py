"""
AI Services - Claude-powered GEO optimization

Features:
- FAQ Generator: Generate smart Q&As from content
- Content Rewriter: Add stats, citations, simplify
- Issue Analyzer: Generate detailed fix recommendations
"""
import re
import json
from typing import Dict, List, Optional
from app.config import settings

# Initialize Anthropic client
client = None
AI_ENABLED = False

try:
    from anthropic import Anthropic
    if settings.anthropic_api_key:
        client = Anthropic(api_key=settings.anthropic_api_key)
        AI_ENABLED = True
except ImportError:
    pass
except Exception:
    pass


def is_ai_enabled() -> bool:
    """Check if AI features are available"""
    return AI_ENABLED


def get_ai_provider() -> Optional[str]:
    """Get current AI provider name"""
    return "anthropic" if AI_ENABLED else None


def call_llm(prompt: str, max_tokens: int = 2000) -> str:
    """
    Call Claude API
    
    Args:
        prompt: The prompt to send
        max_tokens: Maximum tokens in response
        
    Returns:
        The LLM response text
    """
    if not AI_ENABLED or not client:
        raise Exception("AI not enabled. Set ANTHROPIC_API_KEY in .env")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def is_ai_enabled() -> bool:
    """Check if AI features are available"""
    return AI_ENABLED


# ============== FAQ GENERATOR ==============

async def generate_faq(content: str, num_questions: int = 5) -> Dict:
    """
    Generate FAQ section using Claude AI
    
    Returns:
        {
            "faqs": [{"question": "...", "answer": "..."}],
            "schema": "JSON-LD markup",
            "html": "HTML code",
            "ai_generated": bool
        }
    """
    if not AI_ENABLED:
        return {
            "error": "AI features require ANTHROPIC_API_KEY",
            "faqs": [],
            "schema": "",
            "html": "",
            "ai_generated": False
        }
    
    prompt = f"""Analyze this content and generate {num_questions} FAQ questions and answers optimized for AI search engines.

CONTENT:
{content[:5000]}

REQUIREMENTS:
1. Questions should be what real users would ask ChatGPT, Perplexity, or Google
2. Answers should be 2-3 sentences, directly answering the question
3. Include a mix of:
   - "What is..." definitional questions
   - "How to..." procedural questions
   - "Why..." reasoning questions
4. Make answers self-contained (can be quoted without context)
5. Use specific facts from the content, not generic statements

Return ONLY valid JSON (no markdown, no explanation):
{{
    "faqs": [
        {{"question": "What is X?", "answer": "X is... It provides..."}},
        {{"question": "How do I Y?", "answer": "To Y, you need to... First..."}}
    ]
}}"""

    try:
        text = call_llm(prompt, max_tokens=2000)
        text = text.strip()
        
        # Clean markdown if present
        if text.startswith("```"):
            text = re.sub(r'^```json?\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
        
        data = json.loads(text)
        faqs = data.get("faqs", [])
        
        return {
            "faqs": faqs,
            "schema": generate_faq_schema(faqs),
            "html": generate_faq_html(faqs),
            "ai_generated": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "faqs": [],
            "schema": "",
            "html": "",
            "ai_generated": False
        }


def generate_faq_schema(faqs: List[Dict]) -> str:
    """Generate FAQPage JSON-LD schema"""
    if not faqs:
        return ""
    
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


def generate_faq_html(faqs: List[Dict]) -> str:
    """Generate FAQ HTML with microdata"""
    if not faqs:
        return ""
    
    html = '<section class="faq" itemscope itemtype="https://schema.org/FAQPage">\n'
    html += '  <h2>Frequently Asked Questions</h2>\n'
    
    for faq in faqs:
        html += f'''  <details itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
    <summary itemprop="name">{faq["question"]}</summary>
    <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
      <p itemprop="text">{faq["answer"]}</p>
    </div>
  </details>\n'''
    
    html += '</section>'
    return html


# ============== CONTENT REWRITER ==============

async def rewrite_content(
    content: str,
    improvements: List[str],
    issues: Optional[List[Dict]] = None
) -> Dict:
    """
    Rewrite content to improve GEO score using Claude AI
    
    improvements can include:
        - "add_statistics"
        - "add_citations"
        - "add_quotes"
        - "simplify_language"
        - "create_answer_blocks"
        - "add_definitions"
    
    Returns:
        {
            "original": str,
            "rewritten": str,
            "changes": [{"type": "...", "description": "..."}],
            "predicted_score_increase": int
        }
    """
    if not AI_ENABLED:
        return {
            "error": "AI features require ANTHROPIC_API_KEY",
            "original": content,
            "rewritten": None,
            "changes": [],
            "predicted_score_increase": 0
        }
    
    instructions = build_rewrite_instructions(improvements, issues)
    
    prompt = f"""You are a GEO (Generative Engine Optimization) expert. Rewrite this content to make it more likely to be cited by AI assistants like ChatGPT, Claude, and Perplexity.

ORIGINAL CONTENT:
{content[:6000]}

IMPROVEMENTS TO MAKE:
{instructions}

RULES:
1. Preserve the original meaning and key facts
2. Keep the same overall structure and length
3. Make it easy for AI to extract and quote
4. Statistics should be realistic (mark invented ones with [source needed])
5. Answer blocks should be 40-60 words, self-contained
6. Use clear language (8th-10th grade reading level)

Return ONLY valid JSON:
{{
    "rewritten": "The full rewritten content...",
    "changes": [
        {{"type": "added_statistic", "description": "Added X% statistic in paragraph 2"}},
        {{"type": "simplified", "description": "Simplified jargon in introduction"}}
    ],
    "predicted_score_increase": 15
}}"""

    try:
        text = call_llm(prompt, max_tokens=4000)
        text = text.strip()
        
        if text.startswith("```"):
            text = re.sub(r'^```json?\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
        
        result = json.loads(text)
        result["original"] = content
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "original": content,
            "rewritten": None,
            "changes": [],
            "predicted_score_increase": 0
        }


def build_rewrite_instructions(improvements: List[str], issues: Optional[List[Dict]]) -> str:
    """Build improvement instructions for Claude"""
    parts = []
    
    if "add_statistics" in improvements:
        parts.append("""ADD STATISTICS:
- Add 3-5 relevant statistics with percentages or numbers
- Format: "According to [source], X% of..." or "Studies show..."
- Use specific numbers, not vague quantities""")
    
    if "add_citations" in improvements:
        parts.append("""ADD CITATIONS:
- Reference 2-3 credible sources (research, .gov, .edu)
- Use "According to [Source]..." or "Research from [Institution]..."
- Mention specific studies or reports""")
    
    if "add_quotes" in improvements:
        parts.append("""ADD EXPERT QUOTES:
- Add 1-2 expert quotes
- Format: "As [Name], [Title] at [Org], explains: '...'"
- Make quotes specific and insightful""")
    
    if "simplify_language" in improvements:
        parts.append("""SIMPLIFY LANGUAGE:
- Reduce sentences to 15-20 words average
- Replace jargon with plain language
- Use active voice
- Target 8th-10th grade reading level""")
    
    if "create_answer_blocks" in improvements:
        parts.append("""CREATE ANSWER BLOCKS:
- Make key paragraphs 40-60 words
- Each block should answer a question completely
- Start with the main point (inverted pyramid)
- Make blocks self-contained for AI to quote""")
    
    if "add_definitions" in improvements:
        parts.append("""ADD DEFINITIONS:
- Add clear definitions for key terms
- Use "X is defined as..." or "X refers to..."
- Make definitions concise and quotable""")
    
    if issues:
        issue_fixes = [f"- {i['fix']}" for i in issues[:5] if i.get('fix')]
        if issue_fixes:
            parts.append(f"ADDRESS THESE ISSUES:\n" + "\n".join(issue_fixes))
    
    return "\n\n".join(parts)


# ============== ISSUE ANALYZER ==============

async def analyze_issues(content: str, issues: List[Dict]) -> Dict:
    """
    Generate detailed AI analysis and recommendations for issues
    """
    if not AI_ENABLED:
        return {
            "error": "AI features require ANTHROPIC_API_KEY",
            "analysis": None,
            "priority_actions": []
        }
    
    issues_text = "\n".join([
        f"- [{i.get('impact', 'medium').upper()}] {i.get('issue', '')}: {i.get('fix', '')}"
        for i in issues[:10]
    ])
    
    prompt = f"""Analyze these GEO issues and provide specific, actionable recommendations.

CONTENT EXCERPT:
{content[:2000]}

DETECTED ISSUES:
{issues_text}

Provide:
1. Priority ranking of what to fix first
2. Specific examples of how to fix each issue (using the actual content)
3. Estimated time to implement each fix
4. Expected impact on AI visibility

Return ONLY valid JSON:
{{
    "analysis": "Overall assessment of content GEO readiness...",
    "priority_actions": [
        {{
            "rank": 1,
            "issue": "Low statistics density",
            "specific_fix": "In paragraph 2, change 'many users prefer...' to 'According to Gartner, 73% of users prefer...'",
            "time_estimate": "15 minutes",
            "expected_impact": "high"
        }}
    ]
}}"""

    try:
        text = call_llm(prompt, max_tokens=2000)
        text = text.strip()
        
        if text.startswith("```"):
            text = re.sub(r'^```json?\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
        
        return json.loads(text)
        
    except Exception as e:
        return {
            "error": str(e),
            "analysis": None,
            "priority_actions": []
        }


# ============== SCHEMA GENERATORS ==============

def generate_article_schema(
    title: str,
    description: str,
    author: str = "Unknown",
    date_published: Optional[str] = None,
    url: Optional[str] = None
) -> str:
    """Generate Article JSON-LD schema"""
    from datetime import datetime
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title[:110],
        "description": description[:200] if description else "",
        "author": {"@type": "Person", "name": author},
        "datePublished": date_published or datetime.now().strftime("%Y-%m-%d"),
        "dateModified": date_published or datetime.now().strftime("%Y-%m-%d")
    }
    
    if url:
        schema["url"] = url
    
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


def generate_howto_schema(title: str, description: str, steps: List[str]) -> str:
    """Generate HowTo JSON-LD schema"""
    schema = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": title,
        "description": description,
        "step": [
            {"@type": "HowToStep", "position": i + 1, "text": step}
            for i, step in enumerate(steps)
        ]
    }
    
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'
