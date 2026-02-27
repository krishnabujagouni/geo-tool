# GEO Tool - Technical Debt & Improvements

> Last updated: 2026-02-18

## Medium-Term Tasks

### 🔧 Refactoring

#### [ ] Centralize Schema Generators
**Priority:** Medium  
**Effort:** 1-2 hours  
**Files:** `ai_service.py`, `article_generator.py`

Schema generation functions (`generate_faq_schema`, `generate_article_schema`, `generate_howto_schema`) are duplicated across modules.

**Action:**
- Create `app/utils/schema.py` with all schema generators
- Update imports in `ai_service.py` and `article_generator.py`
- Add support for more schema types (Product, Review, Organization)

---

#### [ ] Replace Simple Robots.txt Parser
**Priority:** High  
**Effort:** 2-3 hours  
**File:** `visibility_checker.py`

Current `check_crawler_permission()` uses naive string matching that doesn't handle:
- Wildcards in paths (`*`, `$`)
- Multiple User-agent blocks correctly
- Rule ordering (first match vs most specific)
- Crawl-delay directive

**Action:**
- Install `robotexclusionrulesparser` or `robotstxt-py`
- Replace heuristic parser with proper library
- Add tests for edge cases

**Resources:**
- https://pypi.org/project/robotexclusionrulesparser/
- https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt

---

#### [ ] Improve Framework Detection
**Priority:** Low  
**Effort:** 2-3 hours  
**File:** `ssr_checker.py`

Current detection uses simple string matching which can false-positive (e.g., "astro" in astronomy content).

**Action:**
- Check for specific meta tags/headers
- Inspect script `src` patterns more carefully
- Consider Wappalyzer-style detection or API
- Handle multiple framework indicators

---

### 🧪 Testing

#### [ ] Add Unit Tests for LLM JSON Parsing
**Priority:** High  
**Effort:** 2-3 hours  
**File:** Create `tests/test_ai_service.py`

Test `extract_json_from_response()` with:
- Clean JSON
- Markdown-wrapped JSON (```json ... ```)
- JSON with surrounding text
- Malformed JSON (should raise)
- Nested JSON structures

```python
# Example test cases
def test_extract_json_clean():
    assert extract_json_from_response('{"key": "value"}') == {"key": "value"}

def test_extract_json_markdown():
    assert extract_json_from_response('```json\n{"key": "value"}\n```') == {"key": "value"}

def test_extract_json_with_text():
    assert extract_json_from_response('Here is the result: {"key": "value"} done') == {"key": "value"}
```

---

#### [ ] Add Unit Tests for Robots.txt Parsing
**Priority:** High  
**Effort:** 1-2 hours  
**File:** Create `tests/test_visibility_checker.py`

Test cases:
- All allowed (no robots.txt)
- Specific bot blocked
- Wildcard User-agent
- Path-specific rules
- Multiple User-agent blocks

---

#### [ ] Add Unit Tests for SSR Detection
**Priority:** Medium  
**Effort:** 2-3 hours  
**File:** Create `tests/test_ssr_checker.py`

Test with sample HTML for:
- Next.js SSR page
- React CSR (empty #root)
- WordPress
- Static HTML
- Angular Universal

---

### 📊 Observability

#### [ ] Add Structured Logging for AI Requests
**Priority:** Medium  
**Effort:** 2-3 hours  
**Files:** `ai_service.py`, `article_generator.py`

Log AI requests/responses for debugging (with PII scrubbing):
- Prompt length
- Response length
- Latency
- Token usage (if available)
- Error types

```python
logger.info("LLM request", extra={
    "prompt_chars": len(prompt),
    "max_tokens": max_tokens,
    "endpoint": "generate_faq"
})
```

---

## Completed ✅

### 2026-02-18
- [x] Remove duplicate `is_ai_enabled()` in ai_service.py
- [x] Make `call_llm` non-blocking with `asyncio.to_thread()`
- [x] Fix UnboundLocalError in article_generator.py (`response_text` init)
- [x] Add `extract_json_from_response()` with fallback parsing
- [x] Add error logging for Anthropic client initialization
- [x] Add TODO comments for heuristics in robots/framework detection
- [x] Add rate limiting to all endpoints (slowapi)
- [x] Add AEO (Answer Engine Optimization) scorer and endpoint

---

## Future Features (Backlog)

- [ ] **AI Citation Tracker** — Check if site gets mentioned in ChatGPT/Perplexity responses
- [ ] **PDF Export** — Generate downloadable analysis reports
- [ ] **History/Tracking** — Store past analyses, show score trends
- [ ] **Bulk URL Analysis** — Analyze multiple URLs from sitemap
- [ ] **Browser Extension** — One-click analysis on any page
