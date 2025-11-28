import os
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

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY missing. Add it to a .env file or the environment."
    )

shared_llm = LLM(
    model="gemini-2.0-flash",  # Using Gemini 2.0 Flash model
    api_key=gemini_api_key,
    temperature=0.7,
    timeout=120,
    max_tokens=4000,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
)

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
        url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=ArtList&format=json&maxrecords=50"
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
        for entry in feed.entries[:20]:  # Limit to 20 entries
            articles.append({
                'title': entry.get('title', ''),
                'description': entry.get('description', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'source': feed.feed.get('title', 'RSS Feed')
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
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for post in data.get('data', {}).get('children', []):
                    post_data = post.get('data', {})
                    articles.append({
                        'title': post_data.get('title', ''),
                        'description': post_data.get('selftext', ''),
                        'link': f"https://reddit.com{post_data.get('permalink', '')}",
                        'published': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                        'source': f"Reddit r/{subreddit}",
                        'score': post_data.get('score', 0)
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
        all_articles.append(article)
    
    for article in bbc_news:
        article['source_name'] = 'BBC'
        all_articles.append(article)
    
    for article in reddit_news:
        article['source_name'] = article.get('source', 'Reddit')
        all_articles.append(article)
    
    return all_articles

# Create CrewAI tools using BaseTool
class FetchAllNewsSourcesTool(BaseTool):
    name: str = "fetch_all_news_sources"
    description: str = "Fetch real-time news from all available sources: NewsAPI, NewsData.io, GDELT, Google News RSS, BBC RSS, and Reddit. Returns aggregated news articles with full content and image URLs."
    
    def _run(self) -> str:
        result = aggregate_all_news()
        return json.dumps(result, indent=2, default=str)

class FetchNewsAPITool(BaseTool):
    name: str = "fetch_newsapi_articles"
    description: str = "Fetch top headlines from NewsAPI for India."
    
    def _run(self) -> str:
        result = fetch_newsapi()
        return json.dumps(result, indent=2, default=str)

class FetchNewsDataTool(BaseTool):
    name: str = "fetch_newsdata_articles"
    description: str = "Fetch technology news from NewsData.io."
    
    def _run(self) -> str:
        result = fetch_newsdata()
        return json.dumps(result, indent=2, default=str)

class FetchGDELTTool(BaseTool):
    name: str = "fetch_gdelt_articles"
    description: str = "Fetch global events from GDELT API. Provide a query term to search for specific topics. Call with: fetch_gdelt_articles(query='your_search_term')"
    
    def _run(self, query: str = "world") -> str:
        result = fetch_gdelt(query)
        return json.dumps(result, indent=2, default=str)

class FetchRSSFeedsTool(BaseTool):
    name: str = "fetch_rss_feeds"
    description: str = "Fetch news from Google News RSS and BBC RSS feeds."
    
    def _run(self) -> str:
        google = fetch_google_news_rss()
        bbc = fetch_bbc_rss()
        result = {"google_news": google, "bbc_news": bbc}
        return json.dumps(result, indent=2, default=str)

class FetchRedditNewsTool(BaseTool):
    name: str = "fetch_reddit_news"
    description: str = "Fetch top posts from Reddit subreddits: r/news, r/worldnews, r/technology."
    
    def _run(self) -> str:
        result = fetch_reddit_news()
        return json.dumps(result, indent=2, default=str)

# Instantiate tools
fetch_all_news_sources_tool = FetchAllNewsSourcesTool()
fetch_newsapi_tool = FetchNewsAPITool()
fetch_newsdata_tool = FetchNewsDataTool()
fetch_gdelt_tool = FetchGDELTTool()
fetch_rss_feeds_tool = FetchRSSFeedsTool()
fetch_reddit_news_tool = FetchRedditNewsTool()

# Define three agents with distinct responsibilities
news_researcher = Agent(
    role="Global Events Research Analyst",
    goal="Gather the most significant recent events around the world and rank them by their global importance and impact. Then select the top five events and research each thoroughly using trusted international news sources. Include only original images related to the events from credible sources (no AI-generated images).",
    backstory="You are a professional, precise global news analyst with deep expertise in current affairs. You systematically identify and evaluate worldwide events by their significance and impact, then compile detailed, authoritative reports on the top stories. You source all information and images from reliable international outlets, ensuring included images are original and relevant. Your tone is expert, objective, and well-informed.",
    llm=shared_llm,
    tools=[
        fetch_all_news_sources_tool,
        fetch_newsapi_tool,
        fetch_newsdata_tool,
        fetch_gdelt_tool,
        fetch_rss_feeds_tool,
        fetch_reddit_news_tool
    ],
    verbose=True
)

fact_checker = Agent(
    role="Fact Checker",
    goal="Verify accuracy of claims and flag inconsistencies",
    backstory="Thorough reviewer who cross-checks every statement.",
    llm=shared_llm,
)

copywriter = Agent(
    role="Copywriter",
    goal="Produce a short Flash News brief in a lively tone",
    backstory="Seasoned writer specializing in concise news summaries.",
    llm=shared_llm,
)

# Tasks each agent should perform
research_task = Task(
    description="""
    Use the available tools to fetch real-time news from all available sources:
    - fetch_all_news_sources_tool: Get aggregated news from all sources
    - fetch_newsapi_tool: NewsAPI top headlines
    - fetch_newsdata_tool: NewsData.io technology news
    - fetch_gdelt_tool: GDELT global events (can specify query)
    - fetch_rss_feeds_tool: Google News and BBC RSS feeds
    - fetch_reddit_news_tool: Reddit news from r/news, r/worldnews, r/technology
    
    After collecting all news articles from these sources, rate each event according to:
    1. Global importance (scale 1-10)
    2. Impact level (scale 1-10)
    3. Timeliness/relevance
    
    Select the top 5 events based on combined importance and impact scores.
    
    CRITICAL: For each of the top 5 events, collect and pass COMPLETE information:
    - Full article text/content (DO NOT SUMMARIZE - include the entire article content)
    - Complete descriptions and details
    - Source URLs (multiple sources per event for verification)
    - Original images from the news sources (image URLs from articles, NOT AI-generated)
    - Publication dates and timestamps
    - Author information if available
    - Source names and credibility indicators
    - All relevant metadata
    
    IMPORTANT: Do NOT summarize or condense the information. Pass the full, complete details 
    to the next agent so they can perform thorough fact-checking with all available context.
    
    Format the output as a detailed JSON structure with all collected information for each event.
    """,
    expected_output="""
    A comprehensive JSON structure containing the top 5 global events with complete information:
    {
        "events": [
            {
                "title": "Event title",
                "importance_rating": 1-10,
                "impact_rating": 1-10,
                "combined_score": calculated value,
                "full_content": "Complete article text - NOT summarized",
                "description": "Full description - NOT summarized",
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
    All content must be complete and unsummarized for the fact-checker agent.
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

write_task = Task(
    description="Draft a 150-word Flash News article combining the verified items.",
    expected_output="One cohesive ~150-word Flash News article written in an energetic tone.",
    agent=copywriter,
    async_execution=False  # ensure it runs after validation completes
)

# Assemble the crew and execute
crew = Crew(
    agents=[news_researcher, fact_checker, copywriter],
    tasks=[research_task, validate_task, write_task],
)

result = crew.kickoff()
print(result)
