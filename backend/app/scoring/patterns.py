"""
Regex patterns for GEO scoring detection
"""

# Statistics detection patterns
STAT_PATTERNS = [
    r'\d+\.?\d*\s*%',
    r'\d+\.?\d*\s*(million|billion|trillion)',
    r'\$[\d,]+\.?\d*',
    r'\d+x\s',
    r'(\d+)\s*(out of|of)\s*(\d+)',
    r'(increased|decreased|grew|fell|rose|dropped)\s*(by\s*)?\d+',
    r'\d+\s*(percent|percentage)',
    r'(more|less|over|under|approximately|about|around)\s*\d+',
]

# Quote detection patterns
QUOTE_PATTERNS = [
    r'"[^"]{20,200}"',
    r'"[^"]+"\s*,?\s*(said|says|wrote|stated|explained|noted)\s+[A-Z]',
    r'according to\s+[A-Z][a-z]+',
    r'[A-Z][a-z]+\s+(said|says|notes|explains|argues)',
]

# Definition patterns
DEFINITION_PATTERNS = [
    r'[A-Z][a-zA-Z\s]+\s+is\s+(a|an|the|defined)',
    r'defined as',
    r'refers to',
    r'means that',
]

# Summary signals
SUMMARY_SIGNALS = [
    r'tl;?dr', r'in summary', r'key takeaways?', r'the bottom line',
    r'in short', r"here'?s what you need to know", r'quick summary',
]

# Credible domains
CREDIBLE_DOMAINS = {
    'tier_1': ['.gov', '.edu', 'nature.com', 'sciencedirect.com', 'hbr.org', 
               'mckinsey.com', 'gartner.com', 'statista.com', 'pewresearch.org'],
    'tier_2': ['reuters.com', 'apnews.com', 'bbc.com', 'nytimes.com', 'wsj.com',
               'techcrunch.com', 'wired.com', 'forbes.com', 'bloomberg.com']
}

# AI bots
AI_BOTS = ["GPTBot", "Claude-Web", "ClaudeBot", "PerplexityBot", "Google-Extended", "Amazonbot"]
