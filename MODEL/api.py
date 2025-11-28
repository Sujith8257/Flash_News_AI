from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
from threading import Thread
import time
from model import crew

app = Flask(__name__)

# CORS configuration - allow frontend domain in production
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
CORS(app, origins=[frontend_url, 'http://localhost:5173', 'http://localhost:3000'])

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_ENABLED = os.getenv('SUPABASE_STORAGE_ENABLED', 'false').lower() == 'true'

# Initialize Supabase client if configured
supabase_client = None
if SUPABASE_ENABLED and SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized successfully")
    except ImportError:
        print("⚠️  Supabase package not installed. Install with: pip install supabase")
        SUPABASE_ENABLED = False
    except Exception as e:
        print(f"⚠️  Error initializing Supabase: {e}")
        SUPABASE_ENABLED = False
else:
    print("ℹ️  Supabase storage disabled (using file storage)")

# Articles Storage Configuration
# All articles are stored in the 'articles' folder as individual JSON files
# Each article is saved with its ID as the filename (e.g., 20241215143025.json)
# This ensures articles are never lost and can be easily retrieved
# Articles are NEVER deleted - all articles are permanently saved
ARTICLES_DIR = r'D:\Flash_News_AI\MODEL\articles'

def ensure_articles_dir():
    """Ensure the articles directory exists, create if it doesn't"""
    if not os.path.exists(ARTICLES_DIR):
        try:
            os.makedirs(ARTICLES_DIR)
            print(f"Created articles directory: {ARTICLES_DIR}")
        except Exception as e:
            print(f"Error creating articles directory: {e}")
            raise
    return True

# Create articles directory on startup
ensure_articles_dir()

def load_articles():
    """Load all articles from Supabase (if enabled) or file storage"""
    articles = []
    
    # Try Supabase first if enabled
    if SUPABASE_ENABLED and supabase_client:
        try:
            response = supabase_client.table('articles').select('*').order('created_at', desc=True).execute()
            if response.data:
                for row in response.data:
                    # Convert Supabase row to article format
                    article = {
                        'id': row.get('id'),
                        'title': row.get('title'),
                        'content': row.get('content'),
                        'full_text': row.get('full_text', ''),
                        'created_at': row.get('created_at'),
                        'sources': row.get('sources', []),
                        'images': row.get('images', []),
                        'topics': row.get('topics', []),
                        'related_articles': row.get('related_articles', [])
                    }
                    if article.get('id') and article.get('title'):
                        articles.append(article)
                print(f"✅ Loaded {len(articles)} articles from Supabase")
                return articles
        except Exception as e:
            print(f"⚠️  Error loading from Supabase, falling back to file storage: {e}")
            # Fall through to file storage
    
    # Fallback to file storage
    ensure_articles_dir()
    
    if not os.path.exists(ARTICLES_DIR):
        return articles
    
    try:
        # Get all JSON files in articles directory (exclude temp files)
        files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.json') and not f.endswith('.tmp')]
        
        # Sort by filename (which includes timestamp) in descending order
        files.sort(reverse=True)
        
        for filename in files:
            filepath = os.path.join(ARTICLES_DIR, filename)
            try:
                # Verify file exists and is readable
                if not os.path.exists(filepath):
                    continue
                    
                with open(filepath, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                    # Verify article has required fields
                    if article.get('id') and article.get('title'):
                        articles.append(article)
                    else:
                        print(f"Warning: Article {filename} is missing required fields")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON in {filename}: {e}")
                continue
            except Exception as e:
                print(f"Error loading article {filename}: {e}")
                continue
        
        # Sort by created_at timestamp (newest first)
        articles.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        print(f"📁 Loaded {len(articles)} articles from file storage")
        
    except Exception as e:
        print(f"Error loading articles: {e}")
        import traceback
        traceback.print_exc()
    
    return articles

def save_article(article):
    """Save a single article to Supabase (if enabled) and/or file storage"""
    article_id = article.get('id', datetime.now().strftime("%Y%m%d%H%M%S"))
    if not article_id:
        article_id = datetime.now().strftime("%Y%m%d%H%M%S")
        article['id'] = article_id
    
    # Ensure created_at is set
    if not article.get('created_at'):
        article['created_at'] = datetime.now().isoformat()
    
    success = False
    
    # Try Supabase first if enabled
    if SUPABASE_ENABLED and supabase_client:
        try:
            # Prepare data for Supabase (JSONB columns accept Python lists/dicts directly)
            supabase_data = {
                'id': article_id,
                'title': article.get('title', ''),
                'content': article.get('content', ''),
                'full_text': article.get('full_text', article.get('content', '')),
                'created_at': article.get('created_at'),
                'sources': article.get('sources', []),  # JSONB accepts Python lists
                'images': article.get('images', []),    # JSONB accepts Python lists
                'topics': article.get('topics', []),    # JSONB accepts Python lists
                'related_articles': article.get('related_articles', [])  # JSONB accepts Python lists
            }
            
            # Use upsert to handle both insert and update
            response = supabase_client.table('articles').upsert(supabase_data).execute()
            
            if response.data:
                print(f"✅ Article saved to Supabase: {article_id}")
                success = True
            else:
                print(f"⚠️  Supabase save returned no data")
        except Exception as e:
            print(f"⚠️  Error saving to Supabase: {e}")
            import traceback
            traceback.print_exc()
            # Fall through to file storage
    
    # Always save to file storage as backup (or primary if Supabase disabled)
    try:
        ensure_articles_dir()
        
        filename = f"{article_id}.json"
        filepath = os.path.join(ARTICLES_DIR, filename)
        
        # Use atomic write: write to temp file first, then rename
        temp_filepath = filepath + '.tmp'
        try:
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(article, f, indent=2, ensure_ascii=False)
            
            # Atomic rename (works on most systems)
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_filepath, filepath)
            
            print(f"📁 Article saved to file: {filename}")
            success = True
        except Exception as e:
            # Clean up temp file if rename failed
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except:
                    pass
            if not SUPABASE_ENABLED:
                raise e  # Only raise if Supabase is disabled
        
    except Exception as e:
        print(f"❌ Error saving article to file: {e}")
        import traceback
        traceback.print_exc()
        if not success:  # Only return False if both methods failed
            return False
    
    return success

# Articles are NEVER deleted - all articles are permanently saved
# This function is disabled - articles are never deleted
def delete_old_articles():
    """Articles are never deleted - all articles are permanently saved"""
    # This function does nothing - articles are never deleted
    pass

def extract_topics(title, content):
    """Extract main topics/keywords from article title and content"""
    import re
    # Simple keyword extraction - can be enhanced with NLP
    text = (title + " " + content).lower()
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}
    
    # Extract words (3+ characters, alphanumeric)
    words = re.findall(r'\b[a-z]{3,}\b', text)
    words = [w for w in words if w not in stop_words]
    
    # Count frequency
    from collections import Counter
    word_freq = Counter(words)
    
    # Get top 5-10 keywords as topics
    topics = [word for word, count in word_freq.most_common(10)]
    
    return topics

def find_similar_articles(new_title, new_content, existing_articles, similarity_threshold=0.3):
    """Find articles with similar topics"""
    new_topics = set(extract_topics(new_title, new_content))
    
    similar_articles = []
    for article in existing_articles:
        existing_title = article.get('title', '')
        existing_content = article.get('content', '')
        existing_topics = set(extract_topics(existing_title, existing_content))
        
        # Calculate similarity (Jaccard similarity)
        if len(new_topics) > 0 and len(existing_topics) > 0:
            intersection = len(new_topics & existing_topics)
            union = len(new_topics | existing_topics)
            similarity = intersection / union if union > 0 else 0
            
            if similarity >= similarity_threshold:
                similar_articles.append({
                    'article': article,
                    'similarity': similarity,
                    'common_topics': list(new_topics & existing_topics)
                })
    
    # Sort by similarity (highest first)
    similar_articles.sort(key=lambda x: x['similarity'], reverse=True)
    return similar_articles

def parse_article(result_text):
    """Parse article result into structured format"""
    import re
    article_text = str(result_text)
    sources = []
    images = []
    
    # Extract sources
    if "Sources:" in article_text or "Source:" in article_text:
        sources_section = article_text.split("Sources:")[-1] if "Sources:" in article_text else ""
        if not sources_section:
            sources_section = article_text.split("Source:")[-1] if "Source:" in article_text else ""
        
        for line in sources_section.split('\n'):
            line = line.strip()
            if line and ('http' in line or 'www.' in line):
                if ' - ' in line:
                    parts = line.split(' - ', 1)
                    source_name = parts[0].replace('Source:', '').strip()
                    source_url = parts[1].strip()
                    sources.append({"name": source_name, "url": source_url})
                elif 'http' in line:
                    url = line.split('http')[1] if 'http' in line else line
                    if not url.startswith('http'):
                        url = 'http' + url
                    sources.append({"name": "Source", "url": url})
    
    # Extract image URLs from the article text
    # Look for common image URL patterns - enhanced to catch more variations
    image_patterns = [
        r'https?://[^\s<>"\)]+\.(?:jpg|jpeg|png|gif|webp|svg|bmp)(?:\?[^\s<>"\)]*)?',
        r'https?://[^\s<>"\)]+image[^\s<>"\)]*(?:\.(?:jpg|jpeg|png|gif|webp))?',
        r'https?://[^\s<>"\)]+photo[^\s<>"\)]*(?:\.(?:jpg|jpeg|png|gif|webp))?',
        r'image_url["\']?\s*[:=]\s*["\']?(https?://[^\s<>"\)]+)',
        r'image["\']?\s*[:=]\s*["\']?(https?://[^\s<>"\)]+)',
        r'urlToImage["\']?\s*[:=]\s*["\']?(https?://[^\s<>"\)]+)',
        r'https?://[^\s<>"\)]+/image[s]?/[^\s<>"\)]+',
        r'https?://[^\s<>"\)]+/photo[s]?/[^\s<>"\)]+',
    ]
    
    for pattern in image_patterns:
        matches = re.findall(pattern, article_text, re.IGNORECASE)
        for match in matches:
            img_url = match if isinstance(match, str) else match[0] if match else None
            if img_url:
                # Clean up URL (remove quotes, trailing punctuation)
                img_url = img_url.strip('"\'.,;')
                # Validate it's a real image URL
                if img_url.startswith('http') and img_url not in images:
                    # Check if it looks like an image URL
                    if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '/image', '/photo', 'image', 'photo']) or \
                       any(domain in img_url.lower() for domain in ['imgur', 'flickr', 'unsplash', 'pexels', 'getty']):
                        images.append(img_url)
    
    # Also check if images are mentioned in a structured format
    if "Images:" in article_text or "Image:" in article_text:
        images_section = article_text.split("Images:")[-1] if "Images:" in article_text else ""
        if not images_section:
            images_section = article_text.split("Image:")[-1] if "Image:" in article_text else ""
        
        for line in images_section.split('\n'):
            line = line.strip()
            if line and 'http' in line:
                # Extract URL from line
                url_match = re.search(r'https?://[^\s<>"]+', line)
                if url_match:
                    img_url = url_match.group(0)
                    if img_url not in images:
                        images.append(img_url)
    
    # Extract title
    title = "Flash News: Top Global Events"
    if '\n' in article_text:
        first_line = article_text.split('\n')[0]
        if len(first_line) < 100 and first_line.strip():
            title = first_line.strip()
    
    # Extract content - remove Images and Sources sections
    content = article_text
    if "Sources:" in content:
        content = content.split("Sources:")[0].strip()
    elif "Source:" in content and len(sources) > 0:
        lines = content.split('\n')
        content = '\n'.join([l for l in lines if not any(s['url'] in l for s in sources)])
    
    # Remove Images section from content
    if "Images:" in content:
        content = content.split("Images:")[0].strip()
    elif "Image:" in content:
        # Only remove if it's at the end (part of the structured format)
        if "Image:" in content and ("Sources:" in content or "Source:" in content):
            # Find where Images section starts
            images_start = content.find("Image:")
            sources_start = content.find("Sources:") if "Sources:" in content else content.find("Source:")
            if images_start < sources_start:
                content = content[:images_start].strip()
    
    # Remove image URLs from content if they appear as text
    for img_url in images:
        content = content.replace(img_url, '').strip()
    
    # Clean up and format content
    # Remove multiple consecutive newlines
    import re
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in content.split('\n')]
    content = '\n'.join(lines)
    
    # Remove empty paragraphs
    paragraphs = [p for p in content.split('\n\n') if p.strip()]
    content = '\n\n'.join(paragraphs)
    
    # Clean up title - remove markdown formatting if present
    title = re.sub(r'^#+\s*', '', title).strip()
    title = re.sub(r'\*+', '', title).strip()
    
    # Extract topics from the article
    topics = extract_topics(title, content)
    
    return {
        "title": title,
        "content": content,
        "sources": sources,
        "images": images[:5] if images else [],  # Limit to 5 images max
        "topics": topics,  # Store topics for duplicate detection
        "full_text": article_text
    }

def generate_article_task():
    """Background task to generate article"""
    try:
        print(f"[{datetime.now()}] Starting article generation...")
        
        # Ensure articles directory exists before starting
        ensure_articles_dir()
        
        # Load existing articles to check for duplicates
        existing_articles = load_articles()
        print(f"[{datetime.now()}] Checking {len(existing_articles)} existing articles for similar topics...")
        
        # Generate the article
        result = crew.kickoff()
        article_data = parse_article(result)
        article_data["id"] = datetime.now().strftime("%Y%m%d%H%M%S")
        article_data["created_at"] = datetime.now().isoformat()
        
        # Check for similar articles
        similar_articles = find_similar_articles(
            article_data['title'], 
            article_data['content'], 
            existing_articles,
            similarity_threshold=0.4  # 40% topic overlap considered similar
        )
        
        # If similar articles found, add reference to the most recent one
        if similar_articles:
            most_similar = similar_articles[0]
            prev_article = most_similar['article']
            similarity_score = most_similar['similarity']
            common_topics = most_similar['common_topics']
            
            print(f"[{datetime.now()}] Found similar article: '{prev_article.get('title', 'Unknown')}' (similarity: {similarity_score:.2%})")
            print(f"[{datetime.now()}] Common topics: {', '.join(common_topics[:5])}")
            
            # Check if this is truly a duplicate (very high similarity) or new information
            if similarity_score >= 0.7:
                print(f"[{datetime.now()}] WARNING: Very high similarity ({similarity_score:.2%}) - this might be a duplicate")
                print(f"[{datetime.now()}] Proceeding anyway, but adding reference to previous article")
            
            # Add reference to previous article in the new article
            prev_reference = {
                "id": prev_article.get('id'),
                "title": prev_article.get('title'),
                "created_at": prev_article.get('created_at'),
                "similarity": similarity_score
            }
            article_data["related_articles"] = [prev_reference]
            
            # Add reference text to content
            reference_text = f"\n\n[Related Article: This article relates to a previous article published on {prev_article.get('created_at', 'unknown date')[:10]}: '{prev_article.get('title', 'Previous Article')}']"
            article_data["content"] = article_data["content"] + reference_text
        else:
            print(f"[{datetime.now()}] No similar articles found - this is a new topic")
            article_data["related_articles"] = []
        
        # Save article to file - this is critical, don't proceed if save fails
        if save_article(article_data):
            # Verify the article was actually saved
            filepath = os.path.join(ARTICLES_DIR, f"{article_data['id']}.json")
            if os.path.exists(filepath):
                # Article saved successfully - articles are never deleted
                print(f"[{datetime.now()}] Article generated and saved successfully: {article_data['title']} (ID: {article_data['id']})")
                print(f"[{datetime.now()}] Article saved to: {filepath}")
                print(f"[{datetime.now()}] Article will be permanently stored - never deleted")
                if similar_articles:
                    print(f"[{datetime.now()}] Article references {len(similar_articles)} related article(s)")
            else:
                print(f"[{datetime.now()}] ERROR: Article file not found after save: {filepath}")
        else:
            print(f"[{datetime.now()}] ERROR: Failed to save article: {article_data['title']}")
            print(f"[{datetime.now()}] Article data will be lost!")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR generating article: {str(e)}")
        import traceback
        traceback.print_exc()

def scheduler_worker():
    """Background worker that runs article generation every 30 minutes"""
    while True:
        try:
            generate_article_task()
        except Exception as e:
            print(f"Error in scheduler: {str(e)}")
        
        # Wait 30 minutes (1800 seconds)
        time.sleep(1800)

@app.route('/api/generate-article', methods=['POST'])
def generate_article():
    """Manually trigger article generation"""
    try:
        # Ensure articles directory exists
        ensure_articles_dir()
        
        # Load existing articles to check for duplicates
        existing_articles = load_articles()
        
        # Generate the article
        result = crew.kickoff()
        article_data = parse_article(result)
        article_data["id"] = datetime.now().strftime("%Y%m%d%H%M%S")
        article_data["created_at"] = datetime.now().isoformat()
        
        # Check for similar articles
        similar_articles = find_similar_articles(
            article_data['title'], 
            article_data['content'], 
            existing_articles,
            similarity_threshold=0.4
        )
        
        # If similar articles found, add reference
        if similar_articles:
            most_similar = similar_articles[0]
            prev_article = most_similar['article']
            similarity_score = most_similar['similarity']
            
            # Add reference to previous article
            prev_reference = {
                "id": prev_article.get('id'),
                "title": prev_article.get('title'),
                "created_at": prev_article.get('created_at'),
                "similarity": similarity_score
            }
            article_data["related_articles"] = [prev_reference]
            
            # Add reference text to content
            reference_text = f"\n\n[Related Article: This article relates to a previous article published on {prev_article.get('created_at', 'unknown date')[:10]}: '{prev_article.get('title', 'Previous Article')}']"
            article_data["content"] = article_data["content"] + reference_text
        else:
            article_data["related_articles"] = []
        
        # Save article to file - critical step to prevent data loss
        if save_article(article_data):
            # Verify the article was actually saved
            filepath = os.path.join(ARTICLES_DIR, f"{article_data['id']}.json")
            if os.path.exists(filepath):
                # Article saved successfully - articles are never deleted
                message = f"Article saved to {filepath} (permanently stored - never deleted)"
                if similar_articles:
                    message += f". References {len(similar_articles)} related article(s)."
                return jsonify({
                    "success": True,
                    "article": article_data,
                    "message": message,
                    "similar_articles_found": len(similar_articles)
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": f"Article file not found after save: {filepath}"
                }), 500
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save article to disk"
            }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/articles', methods=['GET'])
def get_articles():
    """Get all articles (newest first)"""
    try:
        articles = load_articles()
        return jsonify({
            "success": True,
            "articles": articles
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/article/<article_id>', methods=['GET'])
def get_article(article_id):
    """Get a specific article by ID"""
    try:
        articles = load_articles()
        article = next((a for a in articles if a.get('id') == article_id), None)
        
        if article:
            return jsonify({
                "success": True,
                "article": article
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Article not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/article', methods=['GET'])
def get_latest_article():
    """Get the latest generated article"""
    try:
        articles = load_articles()
        if articles:
            return jsonify({
                "success": True,
                "article": articles[0]
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "No articles found yet."
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Ensure articles directory exists on startup
    ensure_articles_dir()
    print(f"Articles storage directory ready: {os.path.abspath(ARTICLES_DIR)}")
    print(f"Articles are permanently stored at: {ARTICLES_DIR}")
    print("IMPORTANT: Articles are NEVER deleted - all articles are permanently saved")
    
    # Load existing articles to verify storage is working
    existing_articles = load_articles()
    print(f"Found {len(existing_articles)} existing articles in permanent storage")
    
    # Start background scheduler for automatic article generation
    scheduler_thread = Thread(target=scheduler_worker, daemon=True)
    scheduler_thread.start()
    print("Background scheduler started. Articles will be generated every 30 minutes.")
    print("All articles will be automatically saved and NEVER deleted.")
    
    # Generate first article immediately (only if not in production or if explicitly enabled)
    # In production, the wsgi.py will handle initial article generation
    if os.getenv('FLASK_ENV') != 'production' or os.getenv('GENERATE_INITIAL_ARTICLE', 'false').lower() == 'true':
        print("Generating initial article...")
        generate_article_task()
    
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    app.run(debug=debug, port=port, host='0.0.0.0')

