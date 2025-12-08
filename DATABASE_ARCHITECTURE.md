# Database Architecture - Flash News AI

## Overview

The Flash News AI application uses **Supabase PostgreSQL** as its primary database. The database is designed to store AI-generated news articles with rich metadata including sources, images, topics, and relationships.

---

## Database Schema

### Main Table: `articles`

The `articles` table is the core table storing all generated news articles.

#### Table Structure

```
┌─────────────────────┬──────────────┬─────────────────────────────────────────┐
│ Column Name         │ Data Type    │ Description                            │
├─────────────────────┼──────────────┼─────────────────────────────────────────┤
│ id                  │ TEXT (PK)    │ Unique identifier (timestamp-based)   │
│ title               │ TEXT         │ Article title (NOT NULL)                │
│ content             │ TEXT         │ Main article content (NOT NULL)         │
│ content_preview     │ TEXT         │ 4-5 line summary for feed preview       │
│ full_text           │ TEXT         │ Complete article text with sources      │
│ created_at          │ TIMESTAMPTZ  │ Creation timestamp (auto-set)           │
│ updated_at          │ TIMESTAMPTZ  │ Last update timestamp (auto-updated)    │
│ sources             │ JSONB        │ Array of source objects                 │
│ images              │ JSONB        │ Array of image URLs                     │
│ topics              │ JSONB        │ Array of topic keywords                 │
│ related_articles    │ JSONB        │ Array of related article references     │
└─────────────────────┴──────────────┴─────────────────────────────────────────┘
```

#### Column Details

**Primary Key:**
- `id` (TEXT): Unique identifier, typically timestamp-based format (e.g., `20251129032059`)

**Text Columns:**
- `title` (TEXT, NOT NULL): The headline/title of the article
- `content` (TEXT, NOT NULL): The main article body/content
- `content_preview` (TEXT): A short 4-5 line summary used in article listings/feeds
- `full_text` (TEXT): Complete article text including sources section

**Timestamp Columns:**
- `created_at` (TIMESTAMPTZ): Automatically set to current timestamp on insert
- `updated_at` (TIMESTAMPTZ): Automatically updated on row modification

**JSONB Columns (for complex data):**
- `sources` (JSONB, default: `[]`): Array of source objects
  ```json
  [
    {"name": "BBC News", "url": "https://bbc.com/article"},
    {"name": "Reuters", "url": "https://reuters.com/article"}
  ]
  ```
- `images` (JSONB, default: `[]`): Array of image URLs
  ```json
  [
    "https://example.com/image1.jpg",
    "https://example.com/image2.png"
  ]
  ```
- `topics` (JSONB, default: `[]`): Array of topic keywords extracted from content
  ```json
  ["technology", "AI", "machine learning", "innovation"]
  ```
- `related_articles` (JSONB, default: `[]`): Array of related article IDs (for linking similar articles)
  ```json
  ["20251129032059", "20251129031500"]
  ```

---

## Indexes

The database includes several indexes for optimized query performance:

### 1. **Created At Index** (for chronological queries)
```sql
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);
```
- **Purpose**: Fast retrieval of articles sorted by creation date (newest first)
- **Usage**: Used in feed/listings to show latest articles

### 2. **Full-Text Search Index** (for title search)
```sql
CREATE INDEX idx_articles_title ON articles USING gin(to_tsvector('english', title));
```
- **Purpose**: Fast full-text search on article titles
- **Type**: GIN (Generalized Inverted Index) for PostgreSQL full-text search
- **Language**: English

### 3. **Topics Index** (for topic-based queries)
```sql
CREATE INDEX idx_articles_topics ON articles USING gin(topics);
```
- **Purpose**: Fast queries filtering by topics
- **Type**: GIN index for JSONB array queries
- **Usage**: Finding articles by specific topics/keywords

---

## Triggers & Functions

### Auto-Update Timestamp Function

**Function:** `update_updated_at_column()`
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
```

**Trigger:** `update_articles_updated_at`
- **Event**: BEFORE UPDATE on `articles` table
- **Action**: Automatically sets `updated_at` to current timestamp
- **Purpose**: Ensures `updated_at` is always current without manual updates

---

## Views

### Article Summaries View

**View:** `article_summaries`
```sql
CREATE OR REPLACE VIEW article_summaries AS
SELECT 
    id,
    title,
    LEFT(content, 500) as content_preview,
    created_at,
    sources,
    images,
    topics,
    related_articles
FROM articles
ORDER BY created_at DESC;
```

**Purpose**: 
- Provides a lightweight view for listing articles
- Excludes `full_text` column to reduce data transfer
- Pre-sorted by creation date (newest first)
- Useful for feed/list views that don't need full article content

---

## Row Level Security (RLS)

### RLS Status
- **Enabled**: Yes (`ALTER TABLE articles ENABLE ROW LEVEL SECURITY;`)

### Security Policies

#### 1. Public Read Access
```sql
CREATE POLICY "Allow public read access" ON articles
    FOR SELECT
    USING (true);
```
- **Access**: Anyone can read/view articles
- **Purpose**: Public news feed access

#### 2. Service Role Insert
```sql
CREATE POLICY "Allow service role insert" ON articles
    FOR INSERT
    WITH CHECK (true);
```
- **Access**: Backend service can insert articles
- **Note**: Requires `service_role` key (not `anon` key)

#### 3. Service Role Update
```sql
CREATE POLICY "Allow service role update" ON articles
    FOR UPDATE
    USING (true);
```
- **Access**: Backend service can update articles
- **Note**: Requires `service_role` key (not `anon` key)

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Article Generation Flow                      │
└─────────────────────────────────────────────────────────────────┘

1. Backend (Flask API)
   │
   ├─► News Aggregation (Multiple Sources)
   │   ├─► NewsAPI
   │   ├─► NewsData.io
   │   ├─► GDELT
   │   ├─► RSS Feeds (Google News, BBC)
   │   └─► Reddit API
   │
   ├─► AI Processing (CrewAI Agents)
   │   ├─► News Researcher Agent
   │   ├─► Fact Checker Agent
   │   └─► Copywriter Agent
   │
   └─► Database Write (Supabase)
       │
       ├─► Insert Article
       │   ├─► id (timestamp-based)
       │   ├─► title, content, content_preview
       │   ├─► sources (JSONB array)
       │   ├─► images (JSONB array)
       │   ├─► topics (JSONB array)
       │   └─► created_at (auto-set)
       │
       └─► Update Related Articles
           └─► related_articles (JSONB array)

┌─────────────────────────────────────────────────────────────────┐
│                    Article Retrieval Flow                       │
└─────────────────────────────────────────────────────────────────┘

Frontend (React)
   │
   ├─► Query Supabase Directly
   │   ├─► Read articles table
   │   ├─► Use indexes for fast queries
   │   └─► Filter by date, topics, etc.
   │
   └─► Display Articles
       ├─► Feed View (uses article_summaries view)
       └─► Article Detail View (full article data)
```

---

## Database Relationships

Currently, the database uses a **single-table design** with:
- **No foreign keys**: Related articles are stored as JSONB arrays of IDs
- **Self-referencing**: `related_articles` column contains IDs from the same table
- **Denormalized**: All article data stored in one table for simplicity

### Future Enhancement Possibilities

If scaling requires normalization:
- Separate `sources` table (for source management)
- Separate `topics` table (for topic taxonomy)
- Junction tables for many-to-many relationships
- Separate `images` table (for image metadata)

---

## Query Patterns

### Common Queries

#### 1. Get Latest Articles (Feed View)
```sql
SELECT * FROM articles 
ORDER BY created_at DESC 
LIMIT 20;
```
**Uses Index**: `idx_articles_created_at`

#### 2. Search Articles by Title
```sql
SELECT * FROM articles 
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'technology');
```
**Uses Index**: `idx_articles_title`

#### 3. Find Articles by Topic
```sql
SELECT * FROM articles 
WHERE topics @> '["technology"]'::jsonb;
```
**Uses Index**: `idx_articles_topics`

#### 4. Get Article Summaries (Lightweight)
```sql
SELECT * FROM article_summaries 
LIMIT 10;
```
**Uses View**: `article_summaries`

#### 5. Get Related Articles
```sql
SELECT * FROM articles 
WHERE id = ANY(
    SELECT jsonb_array_elements_text(related_articles) 
    FROM articles 
    WHERE id = '20251129032059'
);
```

---

## Constraints & Validation

### Table Constraints
- **Primary Key**: `id` must be unique and non-empty
- **NOT NULL**: `title` and `content` are required
- **Default Values**: JSONB columns default to empty arrays `[]`

### Data Validation (Application Level)
- Image URLs validated via regex patterns
- Source objects must have `name` and `url` fields
- Content preview generated automatically (4-5 lines)
- Topics extracted from content using keyword analysis

---

## Storage Modes

The application supports multiple storage modes:

### 1. Supabase Only (Production)
- Articles stored in PostgreSQL database
- File storage used as backup
- Recommended for production deployments

### 2. File Storage Only (Development)
- Articles stored in `MODEL/articles/` folder
- JSON files with same structure
- Useful for local development without database

### 3. Dual Storage (Default)
- Articles saved to both Supabase AND file storage
- Provides redundancy and backup
- File storage acts as fallback

---

## Performance Considerations

### Index Usage
- **Created At Index**: Optimizes chronological queries (most common)
- **Title GIN Index**: Enables fast full-text search
- **Topics GIN Index**: Fast topic-based filtering

### JSONB Benefits
- Efficient storage of arrays and objects
- Supports indexing for fast queries
- Flexible schema for varying data structures
- Native PostgreSQL support

### Query Optimization
- Use `article_summaries` view for list views (excludes `full_text`)
- Limit results with `LIMIT` clause
- Use indexes for filtered queries
- Consider pagination for large result sets

---

## Backup & Recovery

### Supabase Managed Backups
- Automatic daily backups
- Point-in-time recovery available
- Backup retention configurable

### Application-Level Backup
- File storage acts as backup
- JSON files in `MODEL/articles/` folder
- Can be used for manual recovery

---

## Security Considerations

### Access Control
- **Public Read**: Anyone can read articles (RLS policy)
- **Service Role Write**: Only backend with `service_role` key can write
- **No Public Write**: Prevents unauthorized article creation

### Key Management
- **Backend**: Uses `service_role` key (bypasses RLS)
- **Frontend**: Uses `anon` key (respects RLS policies)
- **Never expose**: `service_role` key in client-side code

---

## Database Statistics

### Typical Article Size
- **Title**: ~50-100 characters
- **Content**: ~500-1500 words (~3-10 KB)
- **Content Preview**: ~200-500 characters
- **Sources**: ~5-10 objects (~500 bytes)
- **Images**: ~3-5 URLs (~200 bytes)
- **Topics**: ~5-10 keywords (~200 bytes)
- **Total Row Size**: ~5-15 KB per article

### Scalability
- **PostgreSQL**: Handles millions of rows efficiently
- **Indexes**: Maintain query performance at scale
- **JSONB**: Efficient storage for variable-length arrays
- **Partitioning**: Can partition by date if needed (future enhancement)

---

## Migration & Schema Changes

### Schema Version
- Current version: 1.0
- Schema file: `MODEL/supabase_schema.sql`

### Adding Columns
- Example: `add_content_preview_column.sql` shows how to add new columns
- Always test migrations on development database first
- Consider backward compatibility

### Best Practices
- Use `IF NOT EXISTS` for idempotent migrations
- Test migrations on copy of production data
- Document schema changes
- Version control SQL migrations

---

## Monitoring & Maintenance

### Recommended Monitoring
- Query performance (slow query log)
- Index usage statistics
- Table size growth
- Connection pool usage

### Maintenance Tasks
- Regular VACUUM (automatic in Supabase)
- Analyze tables for query planner
- Monitor index bloat
- Review RLS policy effectiveness

---

## Summary

The Flash News AI database architecture is designed for:
- ✅ **Simplicity**: Single-table design for easy maintenance
- ✅ **Performance**: Multiple indexes for fast queries
- ✅ **Flexibility**: JSONB columns for variable data structures
- ✅ **Scalability**: PostgreSQL handles growth efficiently
- ✅ **Security**: RLS policies control access
- ✅ **Reliability**: Automatic backups and recovery

The architecture supports the application's core functionality of storing and retrieving AI-generated news articles with rich metadata, while maintaining good performance and scalability.

