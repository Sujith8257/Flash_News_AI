from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import re
from datetime import datetime
from threading import Thread
import time
from model import crew

# Groq rate limits (RPM, TPM, RPD, TPD) and response headers:
# https://console.groq.com/docs/rate-limits — org-level; retry-after on 429; x-ratelimit-* often on every response.

class LLMRateLimitError(Exception):
    """Custom exception for LLM provider rate-limit/quota errors."""
    def __init__(self, message, quota_info=None):
        super().__init__(message)
        self.quota_info = quota_info or {}

app = Flask(__name__)

# CORS configuration - allow frontend domain in production
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
CORS(app, origins=[frontend_url, 'http://localhost:5173', 'http://localhost:3000'])

# Supabase Configuration (REQUIRED)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # Should be service_role key for backend

# Initialize Supabase client (REQUIRED)
if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError(
        "SUPABASE_URL and SUPABASE_KEY are required. "
        "Add them as environment variables (Railway: Variables tab). "
        "Use service_role key for backend operations."
    )

try:
    from supabase import create_client, Client
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized successfully")
    print(f"✅ Backend will save articles directly to Supabase: {SUPABASE_URL}")
except ImportError:
    raise ImportError("Supabase package not installed. Install with: pip install supabase")
except Exception as e:
    raise Exception(f"Error initializing Supabase: {e}")

def load_articles():
    """Load all articles from Supabase"""
    articles = []
    
    try:
        response = supabase_client.table('articles').select('*').order('created_at', desc=True).execute()
        if response.data:
            for row in response.data:
                # Convert Supabase row to article format
                # Handle JSONB columns - ensure they're properly converted to lists
                images_data = row.get('images')
                if images_data is None:
                    images_data = []
                elif not isinstance(images_data, list):
                    # If it's a string, try to parse it
                    if isinstance(images_data, str):
                        try:
                            import json
                            images_data = json.loads(images_data)
                        except:
                            images_data = []
                    else:
                        images_data = []
                
                sources_data = row.get('sources')
                if sources_data is None:
                    sources_data = []
                elif not isinstance(sources_data, list):
                    if isinstance(sources_data, str):
                        try:
                            import json
                            sources_data = json.loads(sources_data)
                        except:
                            sources_data = []
                    else:
                        sources_data = []
                
                # Generate content_preview if not present (for backward compatibility)
                content_preview = row.get('content_preview')
                if not content_preview:
                    # Generate preview from content if not stored
                    content_preview = generate_content_preview(row.get('content', ''), max_lines=5, max_chars_per_line=100)
                
                article = {
                    'id': row.get('id'),
                    'title': row.get('title'),
                    'content': row.get('content'),
                    'content_preview': content_preview,  # 4-5 line summary
                    'full_text': row.get('full_text', ''),
                    'created_at': row.get('created_at'),
                    'sources': sources_data,
                    'images': images_data,  # Ensure it's always a list
                    'topics': row.get('topics') if isinstance(row.get('topics'), list) else [],
                    'related_articles': row.get('related_articles') if isinstance(row.get('related_articles'), list) else []
                }
                
                # Debug: Log image count for each article
                if article.get('images'):
                    print(f"📸 Article '{article.get('title', 'Unknown')[:50]}' has {len(article.get('images', []))} image(s)")
                
                if article.get('id') and article.get('title'):
                    articles.append(article)
        print(f"✅ Loaded {len(articles)} articles from Supabase")
    except Exception as e:
        print(f"❌ Error loading articles from Supabase: {e}")
        import traceback
        traceback.print_exc()
    
    return articles

def save_article(article):
    """Save a single article to Supabase"""
    article_id = article.get('id', datetime.now().strftime("%Y%m%d%H%M%S"))
    if not article_id:
        article_id = datetime.now().strftime("%Y%m%d%H%M%S")
        article['id'] = article_id
    
    # Ensure created_at is set
    if not article.get('created_at'):
        article['created_at'] = datetime.now().isoformat()
    
    try:
        # Ensure images are included and properly formatted
        article_images = article.get('images', [])
        if not isinstance(article_images, list):
            article_images = []
        
        # Validate image URLs before saving
        validated_article_images = []
        for img_url in article_images:
            if not img_url or not isinstance(img_url, str):
                continue
            # Clean and validate URL
            img_url = img_url.strip().rstrip('.,;)\'"<>')
            if img_url.startswith('http') and len(img_url) > 10:
                # Check if it looks like a valid image URL
                img_url_lower = img_url.lower()
                if (any(ext in img_url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']) or
                    any(keyword in img_url_lower for keyword in ['/image', '/photo', '/img', '/picture', '/media']) or
                    any(domain in img_url_lower for domain in ['imgur', 'flickr', 'unsplash', 'pexels', 'getty', 'cdn', 'media', 'static', 'cloudinary'])):
                    validated_article_images.append(img_url)
        
        article_images = validated_article_images
        
        # Log images being saved
        if article_images:
            print(f"📸 Saving {len(article_images)} validated image(s) to Supabase:")
            for idx, img_url in enumerate(article_images[:5], 1):  # Show first 5
                print(f"   {idx}. {img_url[:100]}")
        else:
            print("⚠️  WARNING: No valid images found in article data!")
            print("⚠️  Attempting to extract images from full_text as fallback...")
            
            # Try to extract from full_text as last resort
            if article.get('full_text'):
                import re
                full_text = article.get('full_text', '')
                img_patterns = [
                    r'https?://[^\s<>"\)]+\.(?:jpg|jpeg|png|gif|webp|svg|bmp)(?:\?[^\s<>"\)]*)?',
                    r'https?://[^\s<>"\)]+image[^\s<>"\)]*(?:\.(?:jpg|jpeg|png|gif|webp))?',
                    r'https?://[^\s<>"\)]+/image[s]?/[^\s<>"\)]+',
                    r'https?://[^\s<>"\)]+/photo[s]?/[^\s<>"\)]+',
                ]
                for pattern in img_patterns:
                    matches = re.findall(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and match.startswith('http'):
                            # Validate before adding
                            match = match.strip().rstrip('.,;)\'"<>')
                            if len(match) > 10 and match not in article_images:
                                article_images.append(match)
                                print(f"✅ Found image in full_text: {match[:80]}...")
                    if article_images:
                        break
            
            if not article_images:
                print("❌ ERROR: Article has no images after all extraction attempts!")
                print("⚠️  Article will be saved, but it should have at least one image.")
        
        # Generate content_preview if not present
        content_preview = article.get('content_preview')
        if not content_preview:
            content_preview = generate_content_preview(article.get('content', ''), max_lines=5, max_chars_per_line=100)
        
        # Prepare data for Supabase (JSONB columns accept Python lists/dicts directly)
        supabase_data = {
            'id': article_id,
            'title': article.get('title', ''),
            'content': article.get('content', ''),
            'full_text': article.get('full_text', article.get('content', '')),
            'created_at': article.get('created_at'),
            'sources': article.get('sources', []),  # JSONB accepts Python lists
            'images': article_images,  # JSONB accepts Python lists - ensure images are included
            'topics': article.get('topics', []),    # JSONB accepts Python lists
            'related_articles': article.get('related_articles', [])  # JSONB accepts Python lists
        }
        
        # Use upsert to handle both insert and update
        # Try with content_preview first, fallback without it if column doesn't exist
        try:
            # First attempt: include content_preview
            supabase_data_with_preview = {**supabase_data, 'content_preview': content_preview}
            response = supabase_client.table('articles').upsert(supabase_data_with_preview).execute()
        except Exception as upsert_error:
            # Check if error is about missing content_preview column
            error_str = str(upsert_error)
            
            # Try to extract error code and message from various formats
            error_code = ''
            error_message = ''
            
            # Check if error has attributes
            if hasattr(upsert_error, 'code'):
                error_code = str(upsert_error.code)
            if hasattr(upsert_error, 'message'):
                error_message = str(upsert_error.message)
            
            # Check if error string contains a dict representation
            if "'code'" in error_str or '"code"' in error_str:
                try:
                    import re
                    # Try to extract code from string like {'code': 'PGRST204', ...}
                    code_match = re.search(r"['\"]code['\"]\s*:\s*['\"]([^'\"]+)['\"]", error_str)
                    if code_match:
                        error_code = code_match.group(1)
                    # Try to extract message
                    msg_match = re.search(r"['\"]message['\"]\s*:\s*['\"]([^'\"]+)['\"]", error_str)
                    if msg_match:
                        error_message = msg_match.group(1)
                except:
                    pass
            
            # Check for PGRST204 error code or content_preview in error message
            is_content_preview_error = (
                'content_preview' in error_str.lower() or 
                'content_preview' in error_message.lower() or
                'PGRST204' in error_str or 
                error_code == 'PGRST204' or
                'schema cache' in error_str.lower() or
                'schema cache' in error_message.lower()
            )
            
            if is_content_preview_error:
                print("⚠️  content_preview column not found in database. Saving without it...")
                print("💡 Run the migration SQL in Supabase SQL Editor:")
                print("   File: add_content_preview_column.sql")
                print("   Or run: ALTER TABLE articles ADD COLUMN IF NOT EXISTS content_preview TEXT;")
                # Remove content_preview and try again
                response = supabase_client.table('articles').upsert(supabase_data).execute()
            else:
                # Re-raise if it's a different error
                raise
        
        if response.data:
            image_count = len(article_images)
            print(f"✅ Article saved to Supabase: {article_id} - {article.get('title', 'Untitled')[:50]}")
            print(f"   📸 Images saved: {image_count}")
            return True
        else:
            print(f"❌ Supabase save returned no data")
            return False
    except Exception as e:
        print(f"❌ Error saving article to Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False

# Articles are NEVER deleted - all articles are permanently saved
# This function is disabled - articles are never deleted
def delete_old_articles():
    """Articles are never deleted - all articles are permanently saved"""
    # This function does nothing - articles are never deleted
    pass

def generate_content_preview(content, max_lines=5, max_chars_per_line=100):
    """Generate a 4-5 line summary/preview of the article content"""
    if not content:
        return "No preview available"
    
    max_total_chars = max_lines * max_chars_per_line
    
    # Split content into paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    # If we have paragraphs, take first few and create summary
    if paragraphs:
        preview_lines = []
        total_chars = 0
        
        for para in paragraphs[:max_lines]:
            # Clean paragraph - remove extra whitespace
            para = ' '.join(para.split())
            
            # If paragraph is too long, truncate it
            if len(para) > max_chars_per_line:
                # Try to truncate at sentence boundary
                sentences = para.split('. ')
                current_line = ""
                for sentence in sentences:
                    if len(current_line) + len(sentence) + 2 <= max_chars_per_line:
                        if current_line:
                            current_line += ". " + sentence
                        else:
                            current_line = sentence
                    else:
                        if current_line:
                            preview_lines.append(current_line)
                            total_chars += len(current_line)
                            if len(preview_lines) >= max_lines or total_chars >= max_total_chars:
                                break
                        current_line = sentence
                
                if current_line and len(preview_lines) < max_lines:
                    preview_lines.append(current_line)
                    total_chars += len(current_line)
            else:
                preview_lines.append(para)
                total_chars += len(para)
            
            if len(preview_lines) >= max_lines or total_chars >= max_total_chars:
                break
        
        # Join lines and ensure it's not too long
        preview = ' '.join(preview_lines)
        if len(preview) > max_total_chars:
            preview = preview[:max_total_chars].rsplit(' ', 1)[0] + '...'
        
        return preview
    
    # Fallback: if no paragraphs, take first N sentences
    sentences = content.split('. ')
    preview_sentences = []
    for sentence in sentences[:max_lines]:
        cleaned = sentence.strip()
        if cleaned:
            preview_sentences.append(cleaned)
    
    preview = '. '.join(preview_sentences)
    if len(preview) > max_total_chars:
        preview = preview[:max_total_chars].rsplit(' ', 1)[0] + '...'
    
    return preview

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
        r'"image_urls"\s*:\s*\[(.*?)\]',  # JSON array of image URLs
        r'"image_url"\s*:\s*"(https?://[^"]+)"',  # JSON image_url field
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
                       any(domain in img_url.lower() for domain in ['imgur', 'flickr', 'unsplash', 'pexels', 'getty', 'cdn', 'media', 'static']):
                        images.append(img_url)
    
    # Also extract from JSON structures if present
    try:
        # Try to parse as JSON if it contains JSON structures
        if '"image_urls"' in article_text or '"image_url"' in article_text:
            json_matches = re.findall(r'"image_urls"\s*:\s*\[(.*?)\]', article_text, re.IGNORECASE | re.DOTALL)
            for json_match in json_matches:
                # Extract URLs from JSON array
                url_matches = re.findall(r'"(https?://[^"]+)"', json_match)
                for url in url_matches:
                    if url not in images:
                        images.append(url)
    except:
        pass
    
    # Also check if images are mentioned in a structured format
    if "Images:" in article_text or "Image:" in article_text:
        images_section = article_text.split("Images:")[-1] if "Images:" in article_text else ""
        if not images_section:
            images_section = article_text.split("Image:")[-1] if "Image:" in article_text else ""
        
        # Split by Sources: to stop at sources section
        if "Sources:" in images_section:
            images_section = images_section.split("Sources:")[0]
        elif "Source:" in images_section:
            images_section = images_section.split("Source:")[0]
        
        for line in images_section.split('\n'):
            line = line.strip()
            # Handle both "Image: https://..." and just "https://..." formats
            if line:
                # Remove "Image:" prefix if present
                if line.lower().startswith('image:'):
                    line = line[6:].strip()  # Remove "Image:" prefix
                
                # Extract URL from line
                if 'http' in line:
                    url_match = re.search(r'https?://[^\s<>"]+', line)
                    if url_match:
                        img_url = url_match.group(0)
                        # Clean up URL
                        img_url = img_url.rstrip('.,;)\'"')
                        if img_url.startswith('http') and img_url not in images:
                            images.append(img_url)
                            print(f"✅ Extracted image from Images section: {img_url[:80]}...")
    
    # Remove duplicates and invalid URLs
    images = list(dict.fromkeys(images))  # Remove duplicates while preserving order
    
    # Validate and clean URLs
    validated_images = []
    for img_url in images:
        if not img_url or not isinstance(img_url, str):
            continue
        
        # Must start with http/https
        if not img_url.startswith('http'):
            continue
        
        # Must be at least 10 characters
        if len(img_url) < 10:
            continue
        
        # Clean up URL - remove common trailing characters
        img_url = img_url.rstrip('.,;)\'"<>')
        
        # Remove common invalid patterns
        if any(invalid in img_url.lower() for invalid in ['placeholder', 'default', 'none', 'null', 'undefined']):
            continue
        
        # Check if URL looks like an image URL
        # Either has image extension, or contains image-related keywords, or from known image domains
        img_url_lower = img_url.lower()
        is_image_url = (
            any(ext in img_url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.jfif']) or
            any(keyword in img_url_lower for keyword in ['/image', '/photo', '/img', '/picture', '/media']) or
            any(domain in img_url_lower for domain in ['imgur', 'flickr', 'unsplash', 'pexels', 'getty', 'cdn', 'media', 'static', 'cloudinary', 'images.unsplash'])
        )
        
        if is_image_url:
            validated_images.append(img_url)
        else:
            print(f"⚠️  Skipped non-image URL: {img_url[:80]}...")
    
    images = validated_images
    
    # Log extracted images for debugging
    print(f"📸 Extracted {len(images)} valid image URL(s) from article")
    if images:
        for idx, img_url in enumerate(images[:3], 1):
            print(f"   Image {idx}: {img_url[:100]}")
    else:
        print("   ⚠️  WARNING: No valid images extracted from article text!")
        print("   🔍 Checking if images are in full_text...")
    
    # Extract title - try multiple methods
    title = "Flash News: Top Global Events"  # Default fallback
    
    # Method 1: Look for markdown-style headings (# Title)
    heading_match = re.search(r'^#+\s+(.+)$', article_text, re.MULTILINE)
    if heading_match:
        potential_title = heading_match.group(1).strip()
        if 10 <= len(potential_title) <= 150:  # Reasonable title length
            title = potential_title
    
    # Method 2: Check first line if it looks like a title
    if title == "Flash News: Top Global Events" and '\n' in article_text:
        first_line = article_text.split('\n')[0].strip()
        # Remove common prefixes and clean up
        first_line = re.sub(r'^(Breaking News|News|Flash News|Update):\s*', '', first_line, flags=re.IGNORECASE)
        first_line = re.sub(r'^#+\s*', '', first_line).strip()
        
        # Check if first line looks like a title (not too long, not a full sentence)
        if 10 <= len(first_line) <= 150 and not first_line.endswith('.') and not first_line.endswith('!'):
            title = first_line
    
    # Method 3: Look for title patterns in the text
    if title == "Flash News: Top Global Events":
        # Look for lines that might be titles (short, capitalized, at the start)
        lines = article_text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            # Check if line looks like a title
            if (10 <= len(line) <= 150 and 
                not line.endswith('.') and 
                not line.endswith(',') and
                not line.startswith('http') and
                line[0].isupper() if line else False):
                # Additional check: not too many lowercase words (titles are usually shorter phrases)
                words = line.split()
                if len(words) <= 15:  # Titles are usually 15 words or less
                    title = line
                    break
    
    # Clean up title - remove markdown, extra formatting
    title = re.sub(r'^#+\s*', '', title).strip()
    title = re.sub(r'\*+', '', title).strip()
    title = re.sub(r'^["\']|["\']$', '', title).strip()  # Remove quotes
    
    # Ensure title is not empty
    if not title or len(title) < 5:
        title = "Flash News: Top Global Events"
    
    print(f"📰 Extracted article title: {title}")
    
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
    
    # Generate content preview (4-5 line summary)
    content_preview = generate_content_preview(content, max_lines=5, max_chars_per_line=100)
    
    return {
        "title": title,
        "content": content,
        "content_preview": content_preview,  # 4-5 line summary for preview
        "sources": sources,
        "images": images[:5] if images else [],  # Limit to 5 images max
        "topics": topics,  # Store topics for duplicate detection
        "full_text": article_text
    }

def _parse_groq_duration_to_seconds(value: str) -> float | None:
    """Parse Groq header durations like '7.66s' or '2m59.56s' (x-ratelimit-reset-*)."""
    v = value.strip().lower()
    m = re.match(r"^([\d.]+)s$", v)
    if m:
        return float(m.group(1))
    m = re.match(r"^(\d+)m([\d.]+)s$", v)
    if m:
        return int(m.group(1)) * 60 + float(m.group(2))
    m = re.match(r"^(\d+)m$", v)
    if m:
        return int(m.group(1)) * 60
    return None


def _groq_ratelimit_headers_from_error(error: BaseException) -> dict[str, str]:
    """Collect Groq x-ratelimit-* and retry-after from LiteLLM/httpx exception chain."""
    keys = (
        "retry-after",
        "x-ratelimit-limit-requests",
        "x-ratelimit-limit-tokens",
        "x-ratelimit-remaining-requests",
        "x-ratelimit-remaining-tokens",
        "x-ratelimit-reset-requests",
        "x-ratelimit-reset-tokens",
    )
    out: dict[str, str] = {}
    visited: set[int] = set()
    stack: list[BaseException] = [error]
    while stack:
        exc = stack.pop()
        eid = id(exc)
        if eid in visited:
            continue
        visited.add(eid)
        resp = getattr(exc, "response", None)
        if resp is not None:
            h = getattr(resp, "headers", None)
            if h is not None:
                for key in keys:
                    val = h.get(key)
                    if val is not None and key not in out:
                        out[key] = str(val)
        for nxt in (getattr(exc, "__cause__", None), getattr(exc, "__context__", None)):
            if nxt is not None:
                stack.append(nxt)
    return out


def _is_transient_network_error(error: BaseException) -> bool:
    """True for DNS/connect blips (e.g. Windows getaddrinfo 11001) that often succeed on retry."""
    msg = str(error).lower()
    if "getaddrinfo" in msg or "11001" in msg:
        return True
    if "name or service not known" in msg:
        return True
    if "temporary failure in name resolution" in msg:
        return True
    if "connection refused" in msg or "connection reset" in msg:
        return True
    if "timed out" in msg or "timeout" in msg:
        return True
    if "connecterror" in msg.replace(" ", ""):
        return True
    cause = getattr(error, "__cause__", None)
    if cause is not None and cause is not error:
        return _is_transient_network_error(cause)
    return False


def crew_kickoff_with_retries(max_attempts: int = 5, initial_delay: float = 4.0):
    """Run crew.kickoff() with backoff on transient DNS/TCP failures."""
    last_err: BaseException | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return crew.kickoff()
        except Exception as e:
            last_err = e
            if _is_rate_limit_error(e):
                raise
            if attempt < max_attempts and _is_transient_network_error(e):
                delay = min(initial_delay * (2 ** (attempt - 1)), 120.0)
                print(
                    f"[{datetime.now()}] Network/DNS error (attempt {attempt}/{max_attempts}): {e!s}. "
                    f"Retrying in {delay:.0f}s..."
                )
                time.sleep(delay)
                continue
            raise
    assert last_err is not None
    raise last_err


def _is_rate_limit_error(error: Exception) -> bool:
    """Return True if the exception looks like a provider rate-limit/quota error."""
    message = str(error) if error else ""
    message_lower = message.lower()
    compact = message_lower.replace(" ", "").replace("_", "")

    if "ratelimiterror" in compact or "rate_limit_exceeded" in message_lower:
        return True
    if "resource_exhausted" in message_lower:
        return True
    if "too many requests" in message_lower:
        return True
    if "429" in message:
        return True
    if "413" in message and (
        "payload" in message_lower or "too large" in message_lower or "groq" in message_lower
    ):
        return True
    if "tokens per minute" in message_lower or "tpm" in message_lower:
        return True
    if "reduce your message" in message_lower or "message size" in message_lower:
        return True
    if "quota" in message_lower and ("exceeded" in message_lower or "exhausted" in message_lower):
        return True
    return False

def _is_quota_completely_exhausted(error: Exception) -> bool:
    """Check if quota is completely exhausted vs temporary rate-limited."""
    message = str(error) if error else ""
    message_lower = message.lower()
    return (
        "limit: 0" in message_lower or
        "limit:0" in message_lower or
        "quota exceeded" in message_lower or
        "insufficient_quota" in message_lower
    )

def _extract_quota_info(error: Exception) -> dict:
    """Extract rate-limit info from Groq/LiteLLM errors, including HTTP headers when present.

    Groq publishes limits per model (TPM, RPM, etc.) and returns x-ratelimit-* headers;
    retry-after is set on 429. See https://console.groq.com/docs/rate-limits
    """
    message = str(error) if error else ""
    message_lower = message.lower()
    info = {
        "completely_exhausted": False,
        "retry_after": None,
        "quota_type": None,
        "limit": None,
        "error_details": None,
        "groq_ratelimit_headers": {},
    }

    info["completely_exhausted"] = _is_quota_completely_exhausted(error)

    hdrs = _groq_ratelimit_headers_from_error(error)
    if hdrs:
        info["groq_ratelimit_headers"] = hdrs
        ra = hdrs.get("retry-after")
        if ra:
            try:
                info["retry_after"] = float(ra)
            except ValueError:
                pass
        if hdrs.get("x-ratelimit-limit-tokens"):
            try:
                info["tpm_limit"] = int(hdrs["x-ratelimit-limit-tokens"])
            except ValueError:
                pass
        if hdrs.get("x-ratelimit-remaining-tokens") is not None:
            try:
                info["tpm_remaining"] = int(hdrs["x-ratelimit-remaining-tokens"])
            except ValueError:
                pass

    if info["retry_after"] is None:
        reset_tok = hdrs.get("x-ratelimit-reset-tokens")
        if reset_tok:
            parsed = _parse_groq_duration_to_seconds(reset_tok)
            if parsed is not None and parsed > 0:
                info["retry_after"] = min(max(parsed, 2.0), 120.0)

    if info["retry_after"] is None:
        retry_match = re.search(r"retry.*?(\d+(?:\.\d+)?)\s*s", message, re.IGNORECASE)
        if retry_match:
            info["retry_after"] = float(retry_match.group(1))
    if info["retry_after"] is None:
        groq_try = re.search(
            r"try again in\s+(\d+(?:\.\d+)?)\s*s", message_lower, re.IGNORECASE
        )
        if groq_try:
            info["retry_after"] = float(groq_try.group(1))

    if not info["quota_type"]:
        if "tokens per minute" in message_lower or "tpm" in message_lower:
            info["quota_type"] = "tpm"
        elif "free_tier" in message_lower:
            info["quota_type"] = "free_tier"
        elif "per day" in message_lower or "daily" in message_lower:
            info["quota_type"] = "daily"
        elif "requests" in message_lower and "per minute" in message_lower:
            info["quota_type"] = "rpm"
        elif "requests" in message_lower:
            info["quota_type"] = "requests"
        elif "tokens" in message_lower:
            info["quota_type"] = "tokens"

    limit_match = re.search(r"limit:\s*(\d+)", message, re.IGNORECASE)
    if limit_match:
        info["limit"] = int(limit_match.group(1))

    return info

def generate_article_task():
    """Background task to generate article"""
    try:
        print(f"[{datetime.now()}] Starting article generation...")
        
        # Load existing articles to check for duplicates
        existing_articles = load_articles()
        print(f"[{datetime.now()}] Checking {len(existing_articles)} existing articles for similar topics...")
        
        # Generate the article
        try:
            result = crew_kickoff_with_retries()
        except Exception as kickoff_err:
            if _is_rate_limit_error(kickoff_err):
                quota_info = _extract_quota_info(kickoff_err)
                
                # Check if it's truly exhausted or just rate limited
                is_truly_exhausted = quota_info.get("completely_exhausted", False)
                
                # If we have a retry_after time, it's likely just rate limiting, not exhaustion
                retry_after = quota_info.get("retry_after")
                if retry_after and retry_after < 300:  # Less than 5 minutes = rate limit, not exhaustion
                    is_truly_exhausted = False
                
                if is_truly_exhausted:
                    print(f"[{datetime.now()}] ❌ Groq API quota COMPLETELY EXHAUSTED (limit: 0)")
                    print(f"[{datetime.now()}] ⚠️  Provider quota has been fully used. Quota typically resets daily.")
                    print(f"[{datetime.now()}] 💡 Solutions:")
                    print(f"[{datetime.now()}]    1. Wait for daily quota reset (usually at midnight UTC)")
                    print(f"[{datetime.now()}]    2. Add billing/upgrade plan for higher limits")
                    print(f"[{datetime.now()}]    3. Use a different API key with available quota")
                    print(f"[{datetime.now()}]    4. See limits for your org: https://console.groq.com/settings/limits")
                    if retry_after:
                        print(f"[{datetime.now()}] ⏰ API suggests retrying after {retry_after:.1f} seconds")
                    # Raise custom exception so scheduler can handle it
                    raise LLMRateLimitError(
                        "Groq API quota completely exhausted (limit: 0)",
                        quota_info
                    )
                else:
                    # Groq: RPM, TPM, RPD, TPD at org level; 429 + retry-after; x-ratelimit-* headers.
                    backoff_seconds = max(int(retry_after or 60), 2)
                    gh = quota_info.get("groq_ratelimit_headers") or {}
                    if gh:
                        print(f"[{datetime.now()}] Groq x-ratelimit / retry headers: {gh}")
                    print(
                        f"[{datetime.now()}] ⚠️  Groq rate limit (often 429; oversized TPM may return 413). "
                        f"Docs: https://console.groq.com/docs/rate-limits"
                    )
                    print(
                        f"[{datetime.now()}] 📊 Limits are per organization (RPM, TPM, RPD, TPD). "
                        f"Your caps: https://console.groq.com/settings/limits"
                    )
                    if quota_info.get("quota_type") == "tpm":
                        print(
                            f"[{datetime.now()}] 💡 TPM: shorten prompts or pick a higher-TPM model "
                            f"(e.g. llama-3.3-70b-versatile vs openai/gpt-oss-120b per Groq table)."
                        )
                    print(f"[{datetime.now()}] ⏰ Will retry after {backoff_seconds}s ({backoff_seconds/60:.1f} minutes)")
                    quota_info["completely_exhausted"] = False
                    quota_info["retry_after"] = backoff_seconds
                    raise LLMRateLimitError(
                        f"Groq rate limited. Retry after {backoff_seconds}s",
                        quota_info
                    )
            
            # If not a quota error, re-raise the original exception
            print(f"[{datetime.now()}] ERROR generating article: {str(kickoff_err)}")
            raise
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
        
        # If similar articles found, attach metadata only (not shown inside article body)
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
                print(f"[{datetime.now()}] Proceeding anyway; related_articles metadata will list the prior piece")
            
            prev_reference = {
                "id": prev_article.get('id'),
                "title": prev_article.get('title'),
                "created_at": prev_article.get('created_at'),
                "similarity": similarity_score
            }
            article_data["related_articles"] = [prev_reference]
            # Related articles stay in metadata only (related_articles / API)—not injected into body text
        else:
            print(f"[{datetime.now()}] No similar articles found - this is a new topic")
            article_data["related_articles"] = []
        
        # Ensure at least one image is present
        image_count = len(article_data.get('images', []))
        print(f"[{datetime.now()}] 📸 Article contains {image_count} image(s) after parsing")
        
        if image_count == 0:
            print(f"[{datetime.now()}] ⚠️  WARNING: No images found in article!")
            print(f"[{datetime.now()}] 🔍 Attempting to extract images from full_text...")
            
            # If still no images, try to extract from full_text with more aggressive patterns
            if article_data.get('full_text'):
                import re
                full_text = article_data.get('full_text', '')
                
                # More comprehensive image URL patterns
                img_patterns = [
                    r'https?://[^\s<>"\)]+\.(?:jpg|jpeg|png|gif|webp|svg|bmp|jfif)(?:\?[^\s<>"\)]*)?',
                    r'https?://[^\s<>"\)]+image[^\s<>"\)]*(?:\.(?:jpg|jpeg|png|gif|webp))?',
                    r'https?://[^\s<>"\)]+/image[s]?/[^\s<>"\)]+',
                    r'https?://[^\s<>"\)]+/photo[s]?/[^\s<>"\)]+',
                    r'https?://[^\s<>"\)]+/media/[^\s<>"\)]+',
                    r'https?://[^\s<>"\)]+/img/[^\s<>"\)]+',
                    r'https?://[^\s<>"\)]+cdn[^\s<>"\)]+\.(?:jpg|jpeg|png|gif|webp)',
                ]
                
                found_images = []
                for pattern in img_patterns:
                    matches = re.findall(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and match.startswith('http'):
                            # Clean and validate
                            match = match.strip().rstrip('.,;)\'"<>')
                            if len(match) > 10 and match not in found_images:
                                # Additional validation
                                match_lower = match.lower()
                                if (any(ext in match_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']) or
                                    any(keyword in match_lower for keyword in ['/image', '/photo', '/img', '/picture', '/media', 'cdn', 'static'])):
                                    found_images.append(match)
                                    print(f"[{datetime.now()}] ✅ Found image in full_text: {match[:80]}...")
                
                if found_images:
                    article_data['images'] = found_images
                    image_count = len(found_images)
                    print(f"[{datetime.now()}] ✅ Extracted {image_count} image(s) from full_text")
        
        if image_count > 0:
            print(f"[{datetime.now()}] 📸 Final image count: {image_count}")
            for idx, img_url in enumerate(article_data.get('images', [])[:3], 1):
                print(f"[{datetime.now()}]   Image {idx}: {img_url[:100]}")
        else:
            print(f"[{datetime.now()}] ❌ ERROR: Article has no images after all extraction attempts!")
            print(f"[{datetime.now()}] ⚠️  Article will be saved without images.")
            print(f"[{datetime.now()}] 💡 Tip: Check if CrewAI is including images in the article output.")
        
        # Save article to Supabase
        if save_article(article_data):
            print(f"[{datetime.now()}] ✅ Article generated and saved to Supabase: {article_data['title']} (ID: {article_data['id']})")
            print(f"[{datetime.now()}] 📸 Images saved: {image_count}")
            if similar_articles:
                print(f"[{datetime.now()}] Article metadata lists {len(similar_articles)} related article(s)")
        else:
            print(f"[{datetime.now()}] ❌ ERROR: Failed to save article to Supabase: {article_data['title']}")
            print(f"[{datetime.now()}] Article data will be lost!")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR generating article: {str(e)}")
        import traceback
        traceback.print_exc()

def scheduler_worker():
    """Background worker that runs article generation every 30 minutes"""
    print(f"[{datetime.now()}] ✅ Scheduler worker started. Will generate articles every 30 minutes.")
    consecutive_quota_errors = 0
    base_sleep_time = 1800  # 30 minutes in seconds
    sleep_time = base_sleep_time  # Default sleep time
    
    while True:
        try:
            generate_article_task()
            # Reset error counter on success
            consecutive_quota_errors = 0
            sleep_time = base_sleep_time  # Reset to normal interval on success
        except LLMRateLimitError as quota_err:
            # Handle quota errors - distinguish between rate limits and quota exhaustion
            quota_info = quota_err.quota_info
            retry_after = quota_info.get("retry_after")
            is_exhausted = quota_info.get("completely_exhausted", False)
            
            if is_exhausted:
                # Completely exhausted - wait longer (1 hour)
                consecutive_quota_errors += 1
                sleep_time = 3600
                print(f"[{datetime.now()}] 💤 Quota completely exhausted. Sleeping for {sleep_time/60:.0f} minutes before next attempt...")
            elif retry_after and retry_after < 300:
                # Short retry time (< 5 min) = rate limit, not exhaustion
                # Just wait the suggested time and retry - don't use exponential backoff
                sleep_time = int(retry_after) + 5  # Add small buffer
                consecutive_quota_errors = 0  # Reset counter for rate limits
                print(f"[{datetime.now()}] ⏸️  Rate limited (temporary). Waiting {sleep_time}s ({sleep_time/60:.1f} minutes) as suggested by API...")
            else:
                # Longer retry time or no retry time = use exponential backoff
                consecutive_quota_errors += 1
                sleep_time = min(base_sleep_time * (2 ** (consecutive_quota_errors - 1)), 14400)
                if retry_after:
                    sleep_time = max(int(retry_after), sleep_time)
                print(f"[{datetime.now()}] 💤 Rate limited. Sleeping for {sleep_time/60:.1f} minutes (exponential backoff: attempt #{consecutive_quota_errors})...")
        except Exception as e:
            # Other errors - just log and continue with normal interval
            error_str = str(e)
            print(f"[{datetime.now()}] ❌ ERROR in scheduler: {error_str}")
            import traceback
            traceback.print_exc()
            sleep_time = base_sleep_time
            consecutive_quota_errors = 0  # Reset quota error counter on non-quota errors
            print(f"[{datetime.now()}] ⚠️  Non-quota error. Will retry in {sleep_time/60:.0f} minutes...")
        
        # Wait before next attempt
        print(f"[{datetime.now()}] 😴 Scheduler sleeping for {sleep_time/60:.1f} minutes ({sleep_time} seconds)...")
        time.sleep(sleep_time)

@app.route('/api/generate-article', methods=['POST'])
def generate_article():
    """Manually trigger article generation"""
    try:
        # Load existing articles to check for duplicates
        existing_articles = load_articles()
        
        # Generate the article
        try:
            result = crew_kickoff_with_retries()
        except Exception as kickoff_err:
            if _is_rate_limit_error(kickoff_err):
                quota_info = _extract_quota_info(kickoff_err)
                
                if quota_info["completely_exhausted"]:
                    error_message = (
                        "Groq API quota completely exhausted (limit: 0). "
                        "Provider quota has been fully used. "
                        "Quota typically resets daily at midnight UTC. "
                        "Solutions: Wait for daily reset, add billing for higher limits, "
                        "or use a different API key. Org limits: https://console.groq.com/settings/limits"
                    )
                else:
                    retry_after = quota_info.get("retry_after", 1800)
                    error_message = (
                        "Groq rate limit hit (org-level RPM, TPM, RPD, TPD; whichever trips first). "
                        f"Retry after {retry_after:.0f} seconds. "
                        "Docs: https://console.groq.com/docs/rate-limits — "
                        "exact caps: https://console.groq.com/settings/limits"
                    )
                
                return jsonify({
                    "success": False,
                    "error": error_message,
                    "code": 429,
                    "quota_info": quota_info,
                    "retry_after": quota_info.get("retry_after")
                }), 429
            
            # If not a quota error, re-raise
            raise
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
        
        # If similar articles found, store related_articles metadata only (not in body)
        if similar_articles:
            most_similar = similar_articles[0]
            prev_article = most_similar['article']
            similarity_score = most_similar['similarity']
            
            prev_reference = {
                "id": prev_article.get('id'),
                "title": prev_article.get('title'),
                "created_at": prev_article.get('created_at'),
                "similarity": similarity_score
            }
            article_data["related_articles"] = [prev_reference]
            # Related articles stay in metadata only—not appended to article content
        else:
            article_data["related_articles"] = []
        
        # Save article to Supabase
        if save_article(article_data):
            message = f"Article saved to Supabase (ID: {article_data['id']})"
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
                "error": "Failed to save article to Supabase"
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
    # Verify Supabase connection on startup
    print("✅ Backend configured to save articles directly to Supabase")
    print(f"✅ Supabase URL: {SUPABASE_URL}")
    
    # Load existing articles to verify Supabase connection
    existing_articles = load_articles()
    print(f"✅ Found {len(existing_articles)} existing articles in Supabase")
    
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