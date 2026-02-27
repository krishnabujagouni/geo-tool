"""
AEO Scorer - Answer Engine Optimization

Scores content for AI answer extraction:
- Question-Answer Patterns (25 pts): Q&A structure, direct answers
- Snippet Readiness (25 pts): Definitions, lists, tables
- First-Sentence Clarity (20 pts): Summarizes the section
- Quotability (15 pts): Standalone extractable statements
- PAA Coverage (15 pts): Covers related questions

Total: 100 points
"""
import re
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup, Tag

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False


# Question patterns for detecting Q&A structures
QUESTION_PATTERNS = [
    r'^(what|how|why|when|where|who|which|can|is|are|do|does|should|will|would)\s+',
    r'\?$',
    r'^(the\s+)?(best|top|most|ultimate|complete|definitive)\s+',
]

# Definition patterns that AI loves to extract
DEFINITION_PATTERNS = [
    r'\b\w+\s+is\s+(a|an|the|defined as|known as)',
    r'\b\w+\s+refers?\s+to\b',
    r'\b\w+\s+means?\b',
    r'in\s+other\s+words',
    r'simply\s+put',
    r'this\s+is\s+(when|where|how|why)',
]

# Patterns that make content hard to extract (ambiguous pronouns)
AMBIGUOUS_PATTERNS = [
    r'\bthis\b(?!\s+(is|means|refers|includes|shows))',
    r'\bthat\b(?!\s+(is|means|shows|includes))',
    r'\bit\b(?!\s+(is|was|has|can|will|should|may|might))',
    r'\bthey\b',
    r'\bthese\b(?!\s+(are|include|show))',
    r'\bthose\b',
]

# Featured snippet trigger phrases
SNIPPET_TRIGGERS = [
    r'^(here\s+are|there\s+are|the\s+following|these\s+include)',
    r'^(to\s+\w+,?\s+(you\s+)?(need|should|must|can))',
    r'^(the\s+(main|key|primary|best)\s+\w+\s+(are|is|include))',
    r'^\d+[\.\)]\s+',  # Numbered lists
    r'^[\•\-\*]\s+',   # Bullet lists
]


def calculate_aeo_score(url: str, content: str, html: str) -> Dict:
    """
    Calculate Answer Engine Optimization score (0-100)
    
    Measures how well content is structured for AI extraction
    """
    soup = BeautifulSoup(html, 'lxml') if html else None
    
    if not soup or not content:
        return {"score": 0, "max": 100, "breakdown": {}, "issues": []}
    
    # Calculate all category scores
    qa_patterns = score_qa_patterns(content, soup)
    snippet_ready = score_snippet_readiness(content, soup)
    first_sentence = score_first_sentence_clarity(content, soup)
    quotability = score_quotability(content)
    paa = score_paa_coverage(content, soup)
    
    total = (
        qa_patterns["score"] +
        snippet_ready["score"] +
        first_sentence["score"] +
        quotability["score"] +
        paa["score"]
    )
    
    # Word count penalty
    word_count = len(content.split())
    if word_count < 300:
        total = int(total * 0.7)
    elif word_count < 500:
        total = int(total * 0.85)
    
    total = max(0, min(100, total))
    
    # Collect all issues
    all_issues = []
    for cat in [qa_patterns, snippet_ready, first_sentence, quotability, paa]:
        all_issues.extend(cat.get("issues", []))
    
    # Sort by impact
    impact_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_issues.sort(key=lambda x: impact_order.get(x.get("impact", "low"), 4))
    
    # Extract detected questions and answers
    questions_detected = qa_patterns.get("questions_detected", [])
    snippet_blocks = snippet_ready.get("snippet_blocks", [])
    
    return {
        "url": url,
        "score": total,
        "grade": get_grade(total),
        "breakdown": {
            "question_answer_patterns": format_category(qa_patterns),
            "snippet_readiness": format_category(snippet_ready),
            "first_sentence_clarity": format_category(first_sentence),
            "quotability": format_category(quotability),
            "paa_coverage": format_category(paa)
        },
        "issues": all_issues[:10],
        "quick_wins": generate_quick_wins(all_issues),
        "details": {
            "questions_detected": len(questions_detected),
            "questions_with_answers": qa_patterns.get("questions_with_answers", 0),
            "snippet_ready_blocks": len(snippet_blocks),
            "quotable_statements": quotability.get("quotable_count", 0),
            "paa_questions_covered": paa.get("covered_count", 0)
        },
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


def generate_quick_wins(issues: List) -> List[str]:
    """Generate quick win recommendations"""
    wins = []
    for issue in issues[:5]:
        if issue.get("impact") in ["high", "critical"]:
            fix = issue.get("fix", "")
            impact = issue.get("predicted_impact", "")
            if fix:
                wins.append(f"{fix} ({impact})" if impact else fix)
    return wins[:5]


# ============== QUESTION-ANSWER PATTERNS (25 pts) ==============

def score_qa_patterns(content: str, soup: BeautifulSoup) -> Dict:
    """
    Score Q&A patterns: questions in headers with direct answers
    
    AI engines love content that:
    - Has questions as headers (H2/H3)
    - Immediately answers the question in the next paragraph
    - Uses clear, direct language
    """
    issues = []
    score = 0
    questions_detected = []
    questions_with_answers = 0
    
    # Find all headers
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
    
    for header in headers:
        header_text = header.get_text(strip=True)
        
        # Check if header is a question
        is_question = False
        for pattern in QUESTION_PATTERNS:
            if re.search(pattern, header_text, re.I):
                is_question = True
                break
        
        if is_question:
            questions_detected.append({
                "question": header_text,
                "tag": header.name,
                "has_direct_answer": False
            })
            
            # Check if there's a direct answer following
            next_elem = header.find_next_sibling()
            if next_elem and next_elem.name == 'p':
                answer_text = next_elem.get_text(strip=True)
                # Good answer: doesn't start with "Well", "So", etc.
                weak_starts = [r'^(well|so|basically|actually|honestly|you see)', 
                               r'^(it depends|that\'s a (good|great) question)']
                is_weak = any(re.search(p, answer_text, re.I) for p in weak_starts)
                
                if not is_weak and len(answer_text.split()) >= 10:
                    questions_with_answers += 1
                    questions_detected[-1]["has_direct_answer"] = True
    
    # Score based on Q&A patterns found
    q_count = len(questions_detected)
    a_count = questions_with_answers
    
    if q_count >= 5 and a_count >= 4:
        score += 15
    elif q_count >= 3 and a_count >= 2:
        score += 10
    elif q_count >= 1 and a_count >= 1:
        score += 5
    else:
        issues.append({
            "category": "aeo",
            "issue": "No question-answer patterns in headers",
            "impact": "high",
            "fix": "Add H2/H3 headers as questions with direct answers below",
            "predicted_impact": "+8-12 points",
            "example": "## What is SEO?\\nSEO (Search Engine Optimization) is the practice of..."
        })
    
    # Check answer quality (10 pts)
    if a_count > 0:
        answer_ratio = a_count / q_count if q_count > 0 else 0
        if answer_ratio >= 0.8:
            score += 10
        elif answer_ratio >= 0.5:
            score += 6
        else:
            score += 3
            issues.append({
                "category": "aeo",
                "issue": f"Only {a_count}/{q_count} questions have direct answers",
                "impact": "medium",
                "fix": "Add clear, direct answers immediately after question headers",
                "predicted_impact": "+3-5 points"
            })
    
    return {
        "score": min(score, 25),
        "max": 25,
        "issues": issues,
        "questions_detected": questions_detected,
        "questions_with_answers": questions_with_answers
    }


# ============== SNIPPET READINESS (25 pts) ==============

def score_snippet_readiness(content: str, soup: BeautifulSoup) -> Dict:
    """
    Score snippet readiness: content formatted for featured snippets
    
    Checks for:
    - Definition blocks ("X is...")
    - Numbered/bullet lists
    - Tables
    - Concise answer paragraphs (40-60 words)
    """
    issues = []
    score = 0
    snippet_blocks = []
    
    # Definition blocks (0-8)
    definition_count = 0
    for pattern in DEFINITION_PATTERNS:
        matches = re.findall(pattern, content, re.I)
        definition_count += len(matches)
    
    if definition_count >= 5:
        score += 8
    elif definition_count >= 3:
        score += 6
    elif definition_count >= 1:
        score += 3
    else:
        issues.append({
            "category": "aeo",
            "issue": "No definition patterns found",
            "impact": "high",
            "fix": "Add definitions like 'X is defined as...' or 'X refers to...'",
            "predicted_impact": "+4-6 points",
            "example": "GEO (Generative Engine Optimization) is the practice of optimizing content for AI search engines."
        })
    
    # Lists (0-6)
    ordered_lists = soup.find_all('ol')
    unordered_lists = soup.find_all('ul')
    total_lists = len(ordered_lists) + len(unordered_lists)
    
    # Check list quality (items with good content)
    quality_lists = 0
    for lst in ordered_lists + unordered_lists:
        items = lst.find_all('li')
        if len(items) >= 3:
            avg_words = sum(len(li.get_text().split()) for li in items) / len(items)
            if 5 <= avg_words <= 30:
                quality_lists += 1
                snippet_blocks.append({
                    "type": "list",
                    "items": len(items),
                    "location": str(lst)[:100]
                })
    
    if quality_lists >= 3:
        score += 6
    elif quality_lists >= 2:
        score += 4
    elif quality_lists >= 1:
        score += 2
    else:
        issues.append({
            "category": "aeo",
            "issue": "No well-structured lists",
            "impact": "medium",
            "fix": "Add numbered or bullet lists with 3-7 items",
            "predicted_impact": "+3-4 points"
        })
    
    # Tables (0-4)
    tables = soup.find_all('table')
    if len(tables) >= 1:
        score += 4
        for table in tables:
            snippet_blocks.append({"type": "table", "location": str(table)[:100]})
    else:
        issues.append({
            "category": "aeo",
            "issue": "No comparison tables",
            "impact": "low",
            "fix": "Add a comparison table for key concepts",
            "predicted_impact": "+2-3 points"
        })
    
    # Concise answer paragraphs 40-60 words (0-7)
    paragraphs = soup.find_all('p')
    answer_ready = 0
    
    for p in paragraphs:
        text = p.get_text(strip=True)
        word_count = len(text.split())
        
        # Ideal: 40-60 words, starts with substance (not "Well" or "So")
        if 35 <= word_count <= 70:
            weak_starts = [r'^(well|so|basically|actually|now|ok|okay)[\s,]']
            if not any(re.search(pat, text, re.I) for pat in weak_starts):
                answer_ready += 1
                if answer_ready <= 5:  # Track first 5
                    snippet_blocks.append({
                        "type": "answer_paragraph",
                        "words": word_count,
                        "preview": text[:100] + "..."
                    })
    
    if answer_ready >= 8:
        score += 7
    elif answer_ready >= 5:
        score += 5
    elif answer_ready >= 2:
        score += 3
    else:
        issues.append({
            "category": "aeo",
            "issue": f"Only {answer_ready} answer-ready paragraphs (40-60 words)",
            "impact": "medium",
            "fix": "Write concise paragraphs that directly answer questions",
            "predicted_impact": "+3-5 points"
        })
    
    return {
        "score": min(score, 25),
        "max": 25,
        "issues": issues,
        "snippet_blocks": snippet_blocks
    }


# ============== FIRST-SENTENCE CLARITY (20 pts) ==============

def score_first_sentence_clarity(content: str, soup: BeautifulSoup) -> Dict:
    """
    Score first-sentence clarity: do sections start with summaries?
    
    AI often extracts the first 1-2 sentences of a section.
    These should summarize the answer, not be filler.
    """
    issues = []
    score = 0
    
    headers = soup.find_all(['h2', 'h3'])
    sections_checked = 0
    good_openers = 0
    
    weak_openers = [
        r'^(in\s+this\s+(section|article|post))',
        r'^(let\'?s?\s+(talk|discuss|look|dive|explore))',
        r'^(as\s+(we|you)\s+(know|mentioned|discussed))',
        r'^(before\s+we\s+(begin|start|dive))',
        r'^(you\s+(may|might)\s+(be\s+wondering|ask))',
        r'^(have\s+you\s+ever\s+wondered)',
        r'^(it\'?s?\s+(no\s+secret|important|worth))',
        r'^(when\s+it\s+comes\s+to)',
    ]
    
    for header in headers:
        next_elem = header.find_next_sibling()
        if next_elem and next_elem.name == 'p':
            sections_checked += 1
            first_sentence = next_elem.get_text(strip=True).split('.')[0]
            
            # Check if it's a weak opener
            is_weak = any(re.search(p, first_sentence, re.I) for p in weak_openers)
            
            # Check if it's substantive (has a fact, definition, or answer)
            is_substantive = (
                len(first_sentence.split()) >= 8 and
                not is_weak and
                re.search(r'\b(is|are|was|were|means|refers|includes|provides|helps|allows)\b', first_sentence, re.I)
            )
            
            if is_substantive:
                good_openers += 1
    
    if sections_checked > 0:
        ratio = good_openers / sections_checked
        
        if ratio >= 0.8:
            score += 20
        elif ratio >= 0.6:
            score += 15
        elif ratio >= 0.4:
            score += 10
            issues.append({
                "category": "aeo",
                "issue": f"Only {int(ratio*100)}% of sections start with clear answers",
                "impact": "medium",
                "fix": "Start each section with a direct statement, not filler",
                "predicted_impact": "+5-8 points",
                "bad_example": "In this section, we'll discuss SEO...",
                "good_example": "SEO improves your website's visibility in search results by..."
            })
        else:
            score += 5
            issues.append({
                "category": "aeo",
                "issue": "Most sections start with filler text",
                "impact": "high",
                "fix": "Rewrite section openers to immediately provide value",
                "predicted_impact": "+8-12 points"
            })
    else:
        score += 10  # No sections to check
    
    return {
        "score": min(score, 20),
        "max": 20,
        "issues": issues,
        "sections_checked": sections_checked,
        "good_openers": good_openers
    }


# ============== QUOTABILITY (15 pts) ==============

def score_quotability(content: str) -> Dict:
    """
    Score quotability: standalone statements that make sense out of context
    
    AI extracts quotes/snippets. Good quotes:
    - Make sense without surrounding context
    - Avoid vague pronouns (this, it, they)
    - Are between 15-40 words
    - State facts or opinions clearly
    """
    issues = []
    score = 0
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    quotable_count = 0
    ambiguous_count = 0
    
    for sentence in sentences:
        word_count = len(sentence.split())
        
        # Check for ambiguous starts
        ambiguous_start = any(
            re.match(p, sentence, re.I) 
            for p in [r'^(this|that|it|they|these|those)\b']
        )
        
        if ambiguous_start:
            ambiguous_count += 1
            continue
        
        # Check if sentence is quotable
        # - Right length (15-40 words)
        # - Doesn't rely on context
        # - Has substance
        if 12 <= word_count <= 45:
            # Has a clear subject (not starting with pronoun)
            has_subject = re.match(r'^[A-Z][a-z]+\s', sentence)
            # Has a verb
            has_verb = re.search(r'\b(is|are|was|were|has|have|had|can|will|should|may|helps?|provides?|allows?|enables?|improves?)\b', sentence, re.I)
            
            if has_subject and has_verb:
                quotable_count += 1
    
    # Score based on quotable density
    total_sentences = len(sentences)
    if total_sentences > 0:
        quotable_ratio = quotable_count / total_sentences
        ambiguous_ratio = ambiguous_count / total_sentences
        
        if quotable_ratio >= 0.4:
            score += 10
        elif quotable_ratio >= 0.25:
            score += 7
        elif quotable_ratio >= 0.1:
            score += 4
        else:
            issues.append({
                "category": "aeo",
                "issue": "Few quotable/extractable statements",
                "impact": "medium",
                "fix": "Write sentences that make sense out of context",
                "predicted_impact": "+4-6 points"
            })
        
        # Penalty for ambiguous pronouns
        if ambiguous_ratio <= 0.1:
            score += 5
        elif ambiguous_ratio <= 0.2:
            score += 3
        else:
            issues.append({
                "category": "aeo",
                "issue": f"{int(ambiguous_ratio*100)}% of sentences start with vague pronouns",
                "impact": "medium",
                "fix": "Replace 'This is...' with specific subjects like 'SEO is...'",
                "predicted_impact": "+2-3 points",
                "bad_example": "This helps improve rankings.",
                "good_example": "Internal linking helps improve search rankings."
            })
    
    return {
        "score": min(score, 15),
        "max": 15,
        "issues": issues,
        "quotable_count": quotable_count,
        "ambiguous_count": ambiguous_count
    }


# ============== PAA COVERAGE (15 pts) ==============

def score_paa_coverage(content: str, soup: BeautifulSoup) -> Dict:
    """
    Score PAA (People Also Ask) coverage potential
    
    Checks if content covers common question types:
    - What is X?
    - How to X?
    - Why is X important?
    - Best X for Y?
    - X vs Y?
    """
    issues = []
    score = 0
    
    # Common PAA patterns
    paa_patterns = {
        "what_is": [r'\bwhat\s+(is|are)\s+\w+', r'\b\w+\s+is\s+(a|an|the)\b'],
        "how_to": [r'\bhow\s+to\s+\w+', r'\bsteps?\s+to\s+\w+', r'\bguide\s+to\s+\w+'],
        "why": [r'\bwhy\s+(is|are|do|does|should)\s+', r'\bbenefits?\s+of\b', r'\bimportance\s+of\b'],
        "best": [r'\bbest\s+\w+\s+(for|to)\b', r'\btop\s+\d+\s+\w+'],
        "comparison": [r'\bvs\.?\b', r'\bversus\b', r'\bcompared?\s+to\b', r'\bdifference\s+between\b'],
    }
    
    covered = {}
    content_lower = content.lower()
    
    for category, patterns in paa_patterns.items():
        for pattern in patterns:
            if re.search(pattern, content_lower, re.I):
                covered[category] = True
                break
    
    covered_count = len(covered)
    
    # Score based on coverage
    if covered_count >= 4:
        score += 15
    elif covered_count >= 3:
        score += 12
    elif covered_count >= 2:
        score += 8
    elif covered_count >= 1:
        score += 4
    else:
        issues.append({
            "category": "aeo",
            "issue": "Content doesn't cover common question types",
            "impact": "high",
            "fix": "Add sections covering 'What is', 'How to', 'Why', and comparisons",
            "predicted_impact": "+6-10 points"
        })
    
    # Suggest missing types
    missing = []
    type_names = {
        "what_is": "What is X?",
        "how_to": "How to X?",
        "why": "Why X? / Benefits",
        "best": "Best X for Y",
        "comparison": "X vs Y"
    }
    
    for ptype, name in type_names.items():
        if ptype not in covered:
            missing.append(name)
    
    if missing and covered_count < 4:
        issues.append({
            "category": "aeo",
            "issue": f"Missing question types: {', '.join(missing[:3])}",
            "impact": "medium",
            "fix": f"Add sections covering: {missing[0]}",
            "predicted_impact": "+2-4 points"
        })
    
    return {
        "score": min(score, 15),
        "max": 15,
        "issues": issues,
        "covered_count": covered_count,
        "covered_types": list(covered.keys()),
        "missing_types": missing
    }
