from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
from threading import Thread
import time
from model import crew

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

ARTICLES_DIR = 'articles'

# Create articles directory if it doesn't exist
if not os.path.exists(ARTICLES_DIR):
    os.makedirs(ARTICLES_DIR)

def load_articles():
    """Load all articles from folder"""
    articles = []
    if not os.path.exists(ARTICLES_DIR):
        return articles
    
    try:
        # Get all JSON files in articles directory
        files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.json')]
        
        # Sort by filename (which includes timestamp) in descending order
        files.sort(reverse=True)
        
        for filename in files:
            filepath = os.path.join(ARTICLES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                    articles.append(article)
            except Exception as e:
                print(f"Error loading article {filename}: {e}")
                continue
        
        # Sort by created_at timestamp (newest first)
        articles.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
    except Exception as e:
        print(f"Error loading articles: {e}")
    
    return articles

def save_article(article):
    """Save a single article to a file in the articles folder"""
    try:
        article_id = article.get('id', datetime.now().strftime("%Y%m%d%H%M%S"))
        filename = f"{article_id}.json"
        filepath = os.path.join(ARTICLES_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving article: {e}")
        return False

def delete_old_articles(max_articles=50):
    """Delete old articles if we exceed the maximum number"""
    articles = load_articles()
    if len(articles) > max_articles:
        # Keep only the newest articles
        articles_to_keep = articles[:max_articles]
        articles_to_delete = articles[max_articles:]
        
        # Delete old article files
        for article in articles_to_delete:
            article_id = article.get('id')
            if article_id:
                filename = f"{article_id}.json"
                filepath = os.path.join(ARTICLES_DIR, filename)
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"Deleted old article: {filename}")
                except Exception as e:
                    print(f"Error deleting article {filename}: {e}")

def parse_article(result_text):
    """Parse article result into structured format"""
    article_text = str(result_text)
    sources = []
    
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
    elif "Source:" in content and len(sources) > 0:
        lines = content.split('\n')
        content = '\n'.join([l for l in lines if not any(s['url'] in l for s in sources)])
    
    return {
        "title": title,
        "content": content,
        "sources": sources,
        "full_text": article_text
    }

def generate_article_task():
    """Background task to generate article"""
    try:
        print(f"[{datetime.now()}] Starting article generation...")
        result = crew.kickoff()
        article_data = parse_article(result)
        article_data["id"] = datetime.now().strftime("%Y%m%d%H%M%S")
        article_data["created_at"] = datetime.now().isoformat()
        
        # Save article to file
        if save_article(article_data):
            # Clean up old articles if needed
            delete_old_articles(max_articles=50)
            print(f"[{datetime.now()}] Article generated successfully: {article_data['title']} (ID: {article_data['id']})")
        else:
            print(f"[{datetime.now()}] Failed to save article: {article_data['title']}")
    except Exception as e:
        print(f"[{datetime.now()}] Error generating article: {str(e)}")

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
        result = crew.kickoff()
        article_data = parse_article(result)
        article_data["id"] = datetime.now().strftime("%Y%m%d%H%M%S")
        article_data["created_at"] = datetime.now().isoformat()
        
        # Save article to file
        if save_article(article_data):
            # Clean up old articles if needed
            delete_old_articles(max_articles=50)
            return jsonify({
                "success": True,
                "article": article_data
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save article"
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
    # Start background scheduler for automatic article generation
    scheduler_thread = Thread(target=scheduler_worker, daemon=True)
    scheduler_thread.start()
    print("Background scheduler started. Articles will be generated every 30 minutes.")
    
    # Generate first article immediately
    print("Generating initial article...")
    generate_article_task()
    
    app.run(debug=True, port=5000, host='0.0.0.0')

