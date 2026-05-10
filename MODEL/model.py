import os
import re
import requests
import json
import feedparser
from datetime import datetime
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
# Avoid extra DNS to telemetry.crewai.com (often flaky on Windows/residential DNS).
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")

groq_base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")


def _parse_groq_api_key_list() -> list[str]:
    """Comma- or newline-separated extra keys from GROQ_API_KEYS."""
    raw = os.getenv("GROQ_API_KEYS", "").strip()
    if not raw:
        return []
    return [p.strip() for p in re.split(r"[\n,]+", raw) if p.strip()]


_groq_api_key_primary = os.getenv("GROQ_API_KEY", "").strip()
_groq_api_key_list = _parse_groq_api_key_list()

if not _groq_api_key_primary and not _groq_api_key_list:
    raise EnvironmentError(
        "Set GROQ_API_KEY and/or GROQ_API_KEYS (comma or newline separated). "
        "Optional per-role: GROQ_API_KEY_RESEARCH, GROQ_API_KEY_FACT_CHECK, GROQ_API_KEY_WRITE, GROQ_API_KEY_IMAGE."
    )


def _resolve_groq_api_key(role_index: int, *role_env_keys: str) -> str:
    """Per-role key env wins; else GROQ_API_KEYS[role_index]; else GROQ_API_KEY (or first list entry)."""
    for env_key in role_env_keys:
        v = os.getenv(env_key, "").strip()
        if v:
            return v
    if role_index < len(_groq_api_key_list):
        return _groq_api_key_list[role_index]
    return _groq_api_key_primary or _groq_api_key_list[0]


research_api_key = _resolve_groq_api_key(0, "GROQ_API_KEY_RESEARCH")
fact_check_api_key = _resolve_groq_api_key(
    1, "GROQ_API_KEY_FACT_CHECK", "GROQ_API_KEY_VALIDATE"
)
write_api_key = _resolve_groq_api_key(2, "GROQ_API_KEY_WRITE")
image_api_key = _resolve_groq_api_key(3, "GROQ_API_KEY_IMAGE")

# Backward compatibility: name used for "primary" pool
groq_api_key = _groq_api_key_primary or _groq_api_key_list[0]


def _normalize_groq_model(model: str) -> str:
    """Ensure LiteLLM uses the Groq provider (not OpenAI) for Groq-hosted IDs."""
    model = (model or "").strip()
    if not model:
        return "groq/llama-3.3-70b-versatile"
    if model.startswith("groq/"):
        return model
    if model.startswith("openai/"):
        return "groq/" + model
    return "groq/" + model


def _int_env(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


_ROLE_MODEL_ENV_KEYS = (
    "GROQ_MODEL_RESEARCH",
    "GROQ_MODEL_FACT_CHECK",
    "GROQ_MODEL_VALIDATE",
    "GROQ_MODEL_WRITE",
    "GROQ_MODEL_IMAGE",
)


def _any_explicit_role_model_env() -> bool:
    return any(os.getenv(k, "").strip() for k in _ROLE_MODEL_ENV_KEYS)


def _resolve_role_model(
    *keys: str,
    builtin_default: str,
    legacy_single: str,
) -> str:
    """Env for this role, else legacy GROQ_MODEL only if *no* role env is set, else builtin.

    Groq TPM/RPM are tracked per model id — use different defaults so research / fact / write
    do not share one 12K TPM bucket (see https://console.groq.com/docs/rate-limits).
    """
    for key in keys:
        v = os.getenv(key, "").strip()
        if v:
            return _normalize_groq_model(v)
    if legacy_single.strip() and not _any_explicit_role_model_env():
        return _normalize_groq_model(legacy_single)
    return _normalize_groq_model(builtin_default)


# Legacy: if GROQ_MODEL is set and no GROQ_MODEL_* vars, all roles use it (single-model mode).
_groq_model_legacy = os.getenv("GROQ_MODEL", "").strip()

# Defaults: three different Groq models → three TPM pools. Scout has higher TPM for long articles.
_DEFAULT_RESEARCH = "llama-3.3-70b-versatile"
_DEFAULT_FACT = "llama-3.1-8b-instant"
_DEFAULT_WRITE = "meta-llama/llama-4-scout-17b-16e-instruct"

research_model = _resolve_role_model(
    "GROQ_MODEL_RESEARCH",
    builtin_default=_DEFAULT_RESEARCH,
    legacy_single=_groq_model_legacy,
)
fact_check_model = _resolve_role_model(
    "GROQ_MODEL_FACT_CHECK",
    "GROQ_MODEL_VALIDATE",
    builtin_default=_DEFAULT_FACT,
    legacy_single=_groq_model_legacy,
)
write_model = _resolve_role_model(
    "GROQ_MODEL_WRITE",
    builtin_default=_DEFAULT_WRITE,
    legacy_single=_groq_model_legacy,
)
image_model = _resolve_role_model(
    "GROQ_MODEL_IMAGE",
    builtin_default=_DEFAULT_FACT,
    legacy_single=_groq_model_legacy,
)

def _key_fingerprint(k: str) -> str:
    if len(k) <= 10:
        return "****"
    return f"{k[:4]}…{k[-4:]}"


print(
    f"✅ Groq LLMs: research={research_model} | fact_check={fact_check_model} | "
    f"image={image_model} | write={write_model}"
)
print(
    f"✅ Groq API keys (fingerprints): research={_key_fingerprint(research_api_key)} | "
    f"fact_check={_key_fingerprint(fact_check_api_key)} | "
    f"image={_key_fingerprint(image_api_key)} | write={_key_fingerprint(write_api_key)}"
)

_base_max_tokens = _int_env("GROQ_MAX_TOKENS", 8192)


def _make_groq_llm(model: str, max_tokens: int, api_key: str) -> LLM:
    return LLM(
        model=model,
        api_key=api_key,
        base_url=groq_base_url,
        temperature=0.7,
        timeout=120,
        max_tokens=max_tokens,
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1,
    )


research_llm = _make_groq_llm(
    research_model,
    _int_env("GROQ_MAX_TOKENS_RESEARCH", min(_base_max_tokens, 6144)),
    research_api_key,
)
fact_check_llm = _make_groq_llm(
    fact_check_model,
    _int_env("GROQ_MAX_TOKENS_FACT_CHECK", min(_base_max_tokens, 4096)),
    fact_check_api_key,
)
copywriter_llm = _make_groq_llm(
    write_model,
    _int_env("GROQ_MAX_TOKENS_WRITE", _base_max_tokens),
    write_api_key,
)
image_llm = _make_groq_llm(
    image_model,
    _int_env("GROQ_MAX_TOKENS_IMAGE", min(_base_max_tokens, 3072)),
    image_api_key,
)

# Backward compatibility for anything importing shared_llm
shared_llm = research_llm

# News API functions
def fetch_newsapi():
    """Fetch news from NewsAPI"""
    try:
        url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=2af46c8507fe47e18b7b2fcd5ef74dce"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])
    except Exception as e:
        print(f"NewsAPI error: {e}")
    return []

def fetch_newsdata():
    """Fetch news from NewsData.io"""
    try:
        url = "https://newsdata.io/api/1/news?apikey=pub_c894654a54c547af95e9f015b256dd28&q=technology"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
    except Exception as e:
        print(f"NewsData.io error: {e}")
    return []

def fetch_gdelt(query="world"):
    """Fetch news from GDELT"""
    try:
        url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=ArtList&format=json&maxrecords=25"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])
    except Exception as e:
        print(f"GDELT error: {e}")
    return []

def fetch_rss_feed(url):
    """Fetch news from RSS feed"""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:12]:  # Keep RSS small for LLM context limits
            # Extract image from media:content or enclosure
            image_url = ''
            if hasattr(entry, 'media_content'):
                for media in entry.media_content:
                    if media.get('type', '').startswith('image/'):
                        image_url = media.get('url', '')
                        break
            if not image_url and hasattr(entry, 'enclosures'):
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        image_url = enclosure.get('href', '')
                        break
            # Also check for media:thumbnail
            if not image_url and hasattr(entry, 'media_thumbnail'):
                for thumb in entry.media_thumbnail:
                    image_url = thumb.get('url', '')
                    break
            
            articles.append({
                'title': entry.get('title', ''),
                'description': entry.get('description', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'source': feed.feed.get('title', 'RSS Feed'),
                'image_url': image_url
            })
        return articles
    except Exception as e:
        print(f"RSS feed error ({url}): {e}")
    return []

def fetch_google_news_rss():
    """Fetch from Google News RSS"""
    return fetch_rss_feed("https://news.google.com/rss")

def fetch_bbc_rss():
    """Fetch from BBC RSS"""
    return fetch_rss_feed("https://feeds.bbci.co.uk/news/rss.xml")

def fetch_reddit_news():
    """Fetch top posts from Reddit news subreddits"""
    try:
        subreddits = ['news', 'worldnews', 'technology']
        articles = []
        for subreddit in subreddits:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=6"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for post in data.get('data', {}).get('children', []):
                    post_data = post.get('data', {})
                    # Extract image URL from Reddit post
                    image_url = ''
                    # Check preview images
                    if 'preview' in post_data and 'images' in post_data['preview']:
                        if post_data['preview']['images']:
                            image_url = post_data['preview']['images'][0].get('source', {}).get('url', '')
                            # Reddit URLs are escaped, unescape them
                            if image_url:
                                image_url = image_url.replace('&amp;', '&')
                    # Check thumbnail
                    if not image_url:
                        thumbnail = post_data.get('thumbnail', '')
                        if thumbnail and thumbnail not in ['self', 'default', 'nsfw']:
                            image_url = thumbnail
                    # Check URL if it's a direct image link
                    url_link = post_data.get('url', '')
                    if not image_url and url_link:
                        if any(ext in url_link.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            image_url = url_link
                    
                    articles.append({
                        'title': post_data.get('title', ''),
                        'description': post_data.get('selftext', ''),
                        'link': f"https://reddit.com{post_data.get('permalink', '')}",
                        'published': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                        'source': f"Reddit r/{subreddit}",
                        'score': post_data.get('score', 0),
                        'image_url': image_url
                    })
    except Exception as e:
        print(f"Reddit error: {e}")
    return articles

def aggregate_all_news():
    """Fetch from all news sources and aggregate"""
    all_articles = []
    
    # Fetch from APIs
    newsapi_articles = fetch_newsapi()
    newsdata_articles = fetch_newsdata()
    gdelt_articles = fetch_gdelt("world")
    google_news = fetch_google_news_rss()
    bbc_news = fetch_bbc_rss()
    reddit_news = fetch_reddit_news()
    
    # Normalize and add source info
    for article in newsapi_articles:
        article['source_name'] = article.get('source', {}).get('name', 'NewsAPI')
        article['image_url'] = article.get('urlToImage', '')
        all_articles.append(article)
    
    for article in newsdata_articles:
        article['source_name'] = article.get('source_id', 'NewsData.io')
        article['image_url'] = article.get('image_url', '')
        all_articles.append(article)
    
    for article in gdelt_articles:
        article['source_name'] = article.get('source', 'GDELT')
        article['image_url'] = article.get('image', '')
        all_articles.append(article)
    
    for article in google_news:
        article['source_name'] = 'Google News'
        if 'image_url' not in article:
            article['image_url'] = ''
        all_articles.append(article)
    
    for article in bbc_news:
        article['source_name'] = 'BBC'
        if 'image_url' not in article:
            article['image_url'] = ''
        all_articles.append(article)
    
    for article in reddit_news:
        article['source_name'] = article.get('source', 'Reddit')
        if 'image_url' not in article:
            article['image_url'] = ''
        all_articles.append(article)
    
    return all_articles


def _clip_text(text: str | None, max_len: int) -> str:
    if not text:
        return ""
    t = str(text).strip().replace("\n", " ")
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def _tool_json(data) -> str:
    """Compact JSON for tool outputs (saves tokens vs indent=2)."""
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=str)


# Create CrewAI tools using BaseTool
class FetchAllNewsSourcesTool(BaseTool):
    name: str = "fetch_all_news_sources"
    description: str = "Fetch real-time news from all available sources: NewsAPI, NewsData.io, GDELT, Google News RSS, BBC RSS, and Reddit. Returns aggregated news articles with full content and image URLs. IMPORTANT: Extract and include image_url field from each article."
    
    def _run(self) -> str:
        result = aggregate_all_news()
        # Cap count and field sizes — Groq free/on-demand TPM rejects ~8k+ token requests.
        formatted_result = []
        for article in result[:12]:
            u = article.get("url", "") or article.get("link", "")
            formatted_article = {
                "title": _clip_text(article.get("title", ""), 150),
                "description": _clip_text(
                    article.get("description", "") or article.get("content", ""), 180
                ),
                "url": u[:400] if u else "",
                "image_url": _clip_text(
                    article.get("image_url", "")
                    or article.get("urlToImage", "")
                    or article.get("image", ""),
                    320,
                ),
                "source_name": _clip_text(article.get("source_name", ""), 40),
                "published": _clip_text(
                    str(article.get("published", "") or article.get("publishedAt", "")),
                    28,
                ),
            }
            formatted_result.append(formatted_article)
        return _tool_json(formatted_result)

class FetchNewsAPITool(BaseTool):
    name: str = "fetch_newsapi_articles"
    description: str = "Fetch top headlines from NewsAPI for India. Returns articles with image URLs in urlToImage field."
    
    def _run(self) -> str:
        result = fetch_newsapi()
        formatted = []
        for article in result[:12]:
            formatted.append({
                "title": _clip_text(article.get("title", ""), 180),
                "description": _clip_text(article.get("description", ""), 200),
                "url": _clip_text(article.get("url", ""), 400),
                "image_url": _clip_text(article.get("urlToImage", ""), 400),
                "source": _clip_text(article.get("source", {}).get("name", ""), 40),
                "publishedAt": _clip_text(article.get("publishedAt", ""), 32),
            })
        return _tool_json(formatted)

class FetchNewsDataTool(BaseTool):
    name: str = "fetch_newsdata_articles"
    description: str = "Fetch technology news from NewsData.io. Returns articles with image URLs in image_url field."
    
    def _run(self) -> str:
        result = fetch_newsdata()
        formatted = []
        for article in result[:12]:
            formatted.append({
                "title": _clip_text(article.get("title", ""), 180),
                "description": _clip_text(article.get("description", ""), 200),
                "url": _clip_text(article.get("link", ""), 400),
                "image_url": _clip_text(article.get("image_url", ""), 400),
                "source": _clip_text(article.get("source_id", ""), 40),
                "pubDate": _clip_text(article.get("pubDate", ""), 32),
            })
        return _tool_json(formatted)

class FetchGDELTTool(BaseTool):
    name: str = "fetch_gdelt_articles"
    description: str = "Fetch global events from GDELT API. Provide a query term to search for specific topics. Returns articles with image URLs in image field. Call with: fetch_gdelt_articles(query='your_search_term')"
    
    def _run(self, query: str = "world") -> str:
        result = fetch_gdelt(query)
        formatted = []
        for article in result[:12]:
            formatted.append({
                "title": _clip_text(article.get("title", ""), 180),
                "url": _clip_text(article.get("url", ""), 400),
                "image_url": _clip_text(article.get("image", ""), 400),
                "source": _clip_text(article.get("source", ""), 40),
                "published": _clip_text(article.get("seendate", ""), 24),
            })
        return _tool_json(formatted)

class FetchRSSFeedsTool(BaseTool):
    name: str = "fetch_rss_feeds"
    description: str = "Fetch news from Google News RSS and BBC RSS feeds. Returns articles with image URLs extracted from media content."
    
    def _run(self) -> str:
        google = fetch_google_news_rss()
        bbc = fetch_bbc_rss()

        def _row(a):
            return {
                "title": _clip_text(a.get("title", ""), 180),
                "description": _clip_text(a.get("description", ""), 200),
                "url": _clip_text(a.get("link", ""), 400),
                "image_url": _clip_text(a.get("image_url", ""), 400),
                "published": _clip_text(a.get("published", ""), 32),
            }

        result = {
            "google_news": [_row(a) for a in google[:10]],
            "bbc_news": [_row(a) for a in bbc[:10]],
        }
        return _tool_json(result)

class FetchRedditNewsTool(BaseTool):
    name: str = "fetch_reddit_news"
    description: str = "Fetch top posts from Reddit subreddits: r/news, r/worldnews, r/technology. Returns posts with image URLs from previews or direct image links."
    
    def _run(self) -> str:
        result = fetch_reddit_news()
        formatted = []
        for a in result[:15]:
            formatted.append({
                "title": _clip_text(a.get("title", ""), 180),
                "description": _clip_text(a.get("description", ""), 200),
                "url": _clip_text(a.get("link", ""), 400),
                "image_url": _clip_text(a.get("image_url", ""), 400),
                "source": _clip_text(a.get("source", ""), 40),
                "score": a.get("score", 0),
            })
        return _tool_json(formatted)

# Instantiate tools (researcher uses aggregated fetch only to stay under provider TPM limits)
fetch_all_news_sources_tool = FetchAllNewsSourcesTool()


class FetchImageCandidatesTool(BaseTool):
    name: str = "fetch_image_candidates"
    description: str = (
        "Fetch a compact list of recent news rows with title, article page URL, and image_url only. "
        "Use at most once when prior task output lacks usable https image URLs for an event."
    )

    def _run(self) -> str:
        rows = []
        for article in aggregate_all_news()[:20]:
            img = (
                article.get("image_url")
                or article.get("urlToImage")
                or article.get("image")
                or ""
            )
            if not img or not str(img).startswith("http"):
                continue
            rows.append(
                {
                    "title": _clip_text(article.get("title", ""), 120),
                    "image_url": _clip_text(str(img), 400),
                    "page_url": _clip_text(
                        str(article.get("url") or article.get("link", "")), 400
                    ),
                    "source_name": _clip_text(article.get("source_name", ""), 40),
                }
            )
        return _tool_json(rows[:15])


fetch_image_candidates_tool = FetchImageCandidatesTool()

# Define agents with distinct responsibilities
news_researcher = Agent(
    role="Global Events Research Analyst",
    goal="Gather the most significant recent events around the world and rank them by their global importance and impact. Then select the top five events and research each thoroughly using trusted international news sources. Include only original images related to the events from credible sources (no AI-generated images).",
    backstory="You are a professional, precise global news analyst with deep expertise in current affairs. You systematically identify and evaluate worldwide events by their significance and impact, then compile detailed, authoritative reports on the top stories. You source all information and images from reliable international outlets, ensuring included images are original and relevant. Your tone is expert, objective, and well-informed.",
    llm=research_llm,
    # Single aggregated tool keeps one observation payload and smaller tool schemas (Groq TPM).
    tools=[fetch_all_news_sources_tool],
    verbose=True
)

fact_checker = Agent(
    role="Fact Checker",
    goal="Verify accuracy of claims and flag inconsistencies while keeping each event usable for publication",
    backstory="Thorough reviewer who cross-checks statements and labels confidence—but news feeds are inherently provisional, so you mark status without telling downstream agents to discard entire stories unless sources clearly contradict each other.",
    llm=fact_check_llm,
)

image_curator = Agent(
    role="Visual Assets Curator",
    goal="Produce a clean, verified image plan: one or two https image URLs per top story, tied to real news pages",
    backstory="Photo desk specialist for wire-style briefs. You only use authentic news images (no AI art, no placeholders). You match images to events by headline and source, prefer URLs already validated upstream, and call the image candidate tool only when a story still lacks a usable URL.",
    llm=image_llm,
    tools=[fetch_image_candidates_tool],
    verbose=True,
)

copywriter = Agent(
    role="Copywriter",
    goal="Produce a comprehensive Flash News article in a lively, engaging tone with proper formatting including sources at the bottom",
    backstory="Seasoned writer for fast-moving news briefings. You always deliver a complete article from the materials provided: you never refuse, apologize, or say you cannot write. When verification is mixed, you use careful attribution (e.g. 'reports indicate', 'according to…') instead of withholding the story.",
    llm=copywriter_llm,
)

# Tasks each agent should perform
research_task = Task(
    description="""
    Call the tool `fetch_all_news_sources` ONCE. It already aggregates NewsAPI, NewsData.io,
    GDELT, Google News RSS, BBC RSS, and Reddit. Do not make duplicate fetch calls.

    After you have the tool result, rate each distinct story according to:
    1. Global importance (scale 1-10)
    2. Impact level (scale 1-10)
    3. Timeliness/relevance
    
    Select the top 5 events based on combined importance and impact scores.
    
    CRITICAL: For each of the top 5 events, collect and pass ESSENTIAL information:
    - Concise event summary (max 120 words per event)
    - Key descriptions and details only
    - Source URLs (multiple sources per event for verification)
    - Original images from the news sources (image URLs from articles, NOT AI-generated)
      * Extract image URLs from the news data (urlToImage, image_url, image fields)
      * CRITICAL: You MUST include at least ONE image URL for each of the top 5 events
      * Include images in the output with clear labels like "Image: [URL]" or "Images: [URL1, URL2]"
      * Only include original news images, never AI-generated images
      * If an event has no image in the source data, try to find a related image from other sources covering the same event
    - Publication dates and timestamps
    - Author information if available
    - Source names and credibility indicators
    - All relevant metadata
    
    IMPORTANT: Keep output compact and structured. Do not include huge raw article dumps.
    
    Format the output as a detailed JSON structure with all collected information for each event.
    """,
    expected_output="""
    A compact JSON structure containing the top 5 global events with essential information:
    {
        "events": [
            {
                "title": "Event title",
                "importance_rating": 1-10,
                "impact_rating": 1-10,
                "combined_score": calculated value,
                "summary": "Concise summary (<=120 words)",
                "description": "Essential details",
                "source_urls": ["url1", "url2", ...],
                "image_urls": ["original_image_url1", "original_image_url2", ...],
                "publication_dates": ["date1", "date2", ...],
                "authors": ["author1", ...],
                "source_names": ["source1", "source2", ...],
                "metadata": {all relevant information}
            },
            ... (4 more events)
        ]
    }
    Keep each event compact to avoid oversized LLM payloads.
    """,
    agent=news_researcher
)

validate_task = Task(
    description="""
    Receive the complete, unsummarized event information from the research analyst.
    For each of the top 5 events, perform thorough fact-checking:
    - Verify claims against multiple sources
    - Cross-reference information across different news outlets
    - Check for consistency in reporting
    - Identify any discrepancies or uncertainties
    - Verify image authenticity (ensure they are original news images, not AI-generated)
    - Validate publication dates and source credibility
    
    Mark each event with a verification status and provide detailed notes.
    """,
    expected_output="""
    A verification report in JSON format:
    {
        "verification_results": [
            {
                "event_title": "Title",
                "status": "VERIFIED" or "FLAGGED" or "PARTIALLY_VERIFIED",
                "confidence_score": 0-100,
                "source_agreement": "high/medium/low",
                "discrepancies": ["list of any inconsistencies"],
                "image_verification": "verified_original" or "needs_review",
                "notes": "Detailed verification notes",
                "recommended_action": "proceed" or "review" or "exclude"
            },
            ... (for all 5 events)
        ]
    }
    """,
    agent=fact_checker
)

image_gather_task = Task(
    description="""
    You receive the research analyst's JSON (top 5 events with image_urls) and the fact-checker's verification report.

    Build an image plan for publication:
    - For each of the 5 events, pick 1–2 best **https** image URLs that clearly relate to that story.
    - Prefer URLs from research `image_urls` when verification status is VERIFIED or PARTIALLY_VERIFIED.
    - Skip stock icons, logos-only, or obvious unrelated thumbnails.
    - Do NOT invent or guess URLs. Every URL must appear in prior task output OR in the tool response.

    If any event still has no usable image after reviewing prior output, call `fetch_image_candidates` **at most once**,
    then select matching candidates by title/topic.

    Output **only** valid JSON (no markdown fences):
    {
      "image_plan": [
        {
          "event_title": "string",
          "primary_image_url": "https://..." ,
          "secondary_image_url": null,
          "caption_hint": "short neutral caption",
          "source_name": "outlet name"
        }
      ]
    }
    Include exactly 5 objects in `image_plan` (one per top event). Use null for secondary_image_url if not needed.
    """,
    expected_output="""
    A single JSON object with key "image_plan" (array of 5 items). Each item has event_title, primary_image_url,
    secondary_image_url (or null), caption_hint, source_name. URLs must be https and real.
    """,
    agent=image_curator,
)

write_task = Task(
    description="""
    Using the research analyst's top events, the fact-checker's verification report, AND the Visual Assets Curator's
    `image_plan` JSON, create a comprehensive Flash News article.
    
    You MUST write a full article every time. Do not refuse, decline, or claim there is "nothing verified" to report.
    Include every event from the research output. For VERIFIED items, state them plainly. For PARTIALLY_VERIFIED or FLAGGED,
    still cover them with clear sourcing and cautious wording (multiple outlets, developing story, etc.)—do not drop all content.
    
    CRITICAL: The article MUST start with a clear, engaging headline/title on the FIRST LINE.
    The title should:
    - Be 10-100 characters long
    - Capture the essence of the top 5 global events being covered
    - Be informative, attention-grabbing, and newsworthy
    - NOT end with a period, exclamation mark, or question mark
    - Be on its own line at the very beginning, before any article content
    
    The article should:
    1. Start with an engaging headline/title on the first line
    2. Be written in a lively, energetic tone
    3. Cover all researched events in one cohesive narrative, respecting verification notes without omitting stories
    4. Be well-structured with clear paragraphs
    5. Include relevant details and context
    6. Be comprehensive (500-1500 words)
    
    CRITICAL REQUIREMENT - IMAGES:
    You MUST include at least ONE image URL in the Images section.
    - Use the Visual Assets Curator's `image_plan`: include every non-null primary_image_url (and secondary_image_url when set).
    - Do not substitute different URLs than the image_plan unless a URL is clearly broken; then fall back to research image_urls.
    - Images must be https links from real news pages; no placeholders.
    
    CRITICAL FORMATTING REQUIREMENT:
    Format the article as follows:
    
    [Title/Headline on first line - 10-100 characters, no punctuation at end]
    
    [Article content here - multiple paragraphs]
    
    Images:
    Image: https://example.com/image1.jpg
    Image: https://example.com/image2.jpg
    (MUST include at least one image URL)
    
    Sources:
    Source: BBC News - https://www.bbc.com/news/article1
    Source: Reuters - https://www.reuters.com/article2
    Source: The Guardian - https://www.theguardian.com/article3
    
    Example:
    Global Markets Surge as Tech Giants Announce Breakthrough AI Developments
    
    In a stunning turn of events, major technology companies have unveiled...
    [rest of article content]
    
    Images:
    Image: https://example.com/image1.jpg
    
    Sources:
    Source: BBC News - https://www.bbc.com/news/article1
    """,
    expected_output="""
    A well-formatted Flash News article with:
    - Clear, engaging headline/title on the FIRST LINE (10-100 characters, no ending punctuation)
    - Comprehensive article content (500-1500 words)
    - Lively, energetic writing style
    - Proper paragraph structure
    - Images section with AT LEAST ONE image URL from news sources (REQUIRED - must include at least 1 image)
    - Sources section at the bottom with source names and URLs
    Format: Title on first line, then content, then "Image: [URL]" for images (minimum 1 image required) and "Source: [Name] - [URL]" for sources
    """,
    agent=copywriter,
    async_execution=False  # ensure it runs after validation completes
)

# Assemble the crew and execute
crew = Crew(
    agents=[news_researcher, fact_checker, image_curator, copywriter],
    tasks=[research_task, validate_task, image_gather_task, write_task],
)

# Only run if executed directly (not when imported)
if __name__ == "__main__":
    result = crew.kickoff()
    print(result)
    
    # Save result to file for API access
    try:
        article_text = str(result)
        sources = []
        
        # Extract sources if present
        if "Sources:" in article_text:
            sources_section = article_text.split("Sources:")[-1]
            for line in sources_section.split('\n'):
                line = line.strip()
                if line and ('http' in line or 'www.' in line):
                    if ' - ' in line:
                        parts = line.split(' - ', 1)
                        source_name = parts[0].replace('Source:', '').strip()
                        source_url = parts[1].strip()
                        sources.append({"name": source_name, "url": source_url})
        
        # Extract title
        title = "Flash News: Top Global Events"
        if '\n' in article_text:
            first_line = article_text.split('\n')[0]
            if len(first_line) < 100 and first_line.strip():
                title = first_line.strip()
        
        # Extract content
        content = article_text
        if "Sources:" in content:
            content = content.split("Sources:")[0].strip()
        
        article_data = {
            "title": title,
            "content": content,
            "sources": sources,
            "full_text": article_text
        }
        
        # Only save to file if running locally (not in production)
        if os.getenv('FLASK_ENV') != 'production':
            try:
                with open('latest_article.json', 'w', encoding='utf-8') as f:
                    json.dump(article_data, f, indent=2, ensure_ascii=False)
                print("\nArticle saved to latest_article.json")
            except Exception as e:
                print(f"\nNote: Could not save to file (this is normal in production): {e}")
    except Exception as e:
        print(f"Error saving article: {e}")