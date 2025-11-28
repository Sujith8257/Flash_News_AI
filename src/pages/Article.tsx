import { Link, useParams } from "react-router-dom"
import { useState, useEffect } from "react"
import { fetchArticleFromSupabase, isSupabaseConfigured, type Article } from "../lib/supabase"

export function Article() {
  const { id } = useParams<{ id?: string }>()
  const [article, setArticle] = useState<Article | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchArticle = async () => {
    try {
      setLoading(true)
      setError(null)
      
      if (!id) {
        setError("Article ID is required.")
        return
      }
      
      // Check if Supabase is configured
      if (!isSupabaseConfigured()) {
        setError("Supabase is not configured. Please add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to your .env file.")
        return
      }
      
      // Fetch article directly from Supabase
      const supabaseArticle = await fetchArticleFromSupabase(id)
      
      if (supabaseArticle) {
        setArticle(supabaseArticle)
      } else {
        setError("Article not found.")
      }
    } catch (err) {
      setError("Failed to fetch article from Supabase. Please check your connection and Supabase configuration.")
      console.error("Error fetching article:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchArticle()
  }, [id])

  // Update document title when article is loaded
  useEffect(() => {
    if (article) {
      document.title = `${article.title} - Flash News AI`
    } else {
      document.title = "Article - Flash News AI"
    }
  }, [article])

  // Format content into paragraphs with better structure
  const formatContent = (content: string) => {
    if (!content) return []
    
    // Split by double newlines first
    let paragraphs = content.split('\n\n').filter(p => p.trim().length > 0)
    
    // Further split long paragraphs that might have single newlines
    const formatted: string[] = []
    paragraphs.forEach(para => {
      // If paragraph is very long, try to split by single newlines
      if (para.length > 500 && para.includes('\n')) {
        const subParas = para.split('\n').filter(p => p.trim().length > 0)
        formatted.push(...subParas)
      } else {
        formatted.push(para)
      }
    })
    
    // Clean up paragraphs
    return formatted.map(p => p.trim()).filter(p => p.length > 0)
  }

  return (
    <div className="relative flex min-h-screen w-full flex-col bg-white dark:bg-black text-black dark:text-white">
      <main className="mx-auto w-full max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <style>{`
          .article-content p {
            text-align: justify;
            hyphens: auto;
            -webkit-hyphens: auto;
            -ms-hyphens: auto;
          }
          .article-content p:first-of-type {
            font-size: 1.25rem;
            line-height: 1.9;
            color: rgb(55, 65, 81);
          }
          .dark .article-content p:first-of-type {
            color: rgb(209, 213, 219);
          }
        `}</style>
        <div className="mb-8">
          <Link
            to="/feed"
            className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            <span>Back</span>
          </Link>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <svg className="animate-spin h-8 w-8 mx-auto mb-4 text-gray-600 dark:text-gray-400" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-gray-600 dark:text-gray-400">Loading article...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        {article && !loading && (
          <article className="max-w-none">
            {/* Featured Image */}
            {article.images && article.images.length > 0 && (
              <a 
                href={article.images[0]} 
                target="_blank" 
                rel="noopener noreferrer"
                className="mb-10 rounded-xl overflow-hidden shadow-2xl block hover:shadow-3xl transition-shadow"
                aria-label="View featured image in full size"
              >
                <img
                  src={article.images[0]}
                  alt={article.title}
                  className="w-full h-auto object-cover max-h-[600px] hover:opacity-90 transition-opacity"
                  loading="lazy"
                  onError={(e) => {
                    // Show placeholder if image fails to load
                    const target = e.target as HTMLImageElement
                    target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="400"%3E%3Crect fill="%23ddd" width="800" height="400"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em" font-size="20"%3EImage not available%3C/text%3E%3C/svg%3E'
                    target.className = 'w-full h-auto object-cover max-h-[600px] opacity-50'
                  }}
                />
              </a>
            )}

            {/* Article Header with Title */}
            <header className="mb-10 pb-8 border-b-2 border-gray-200 dark:border-gray-800">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold mb-6 text-black dark:text-white leading-tight tracking-tight">
                {article.title}
              </h1>
              {article.created_at && (
                <div className="space-y-3">
                  <div className="flex items-center gap-4 text-base text-gray-600 dark:text-gray-400">
                    <time dateTime={article.created_at} className="font-medium">
                      Generated: {new Date(article.created_at).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </time>
                    <span className="text-gray-300 dark:text-gray-700">•</span>
                    <span className="font-semibold text-gray-700 dark:text-gray-300">Flash News AI</span>
                  </div>
                  
                  {/* Generation Metadata */}
                  <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-500 pt-2 border-t border-gray-200 dark:border-gray-800">
                    <div className="flex items-center gap-2">
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                      </svg>
                      <span>Article ID: {article.id}</span>
                    </div>
                    {article.sources && article.sources.length > 0 && (
                      <div className="flex items-center gap-2">
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                        <span>{article.sources.length} Source{article.sources.length === 1 ? '' : 's'}</span>
                      </div>
                    )}
                    {article.images && article.images.length > 0 && (
                      <div className="flex items-center gap-2">
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span>{article.images.length} Image{article.images.length === 1 ? '' : 's'}</span>
                      </div>
                    )}
                    {article.topics && article.topics.length > 0 && (
                      <div className="flex items-center gap-2">
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                        </svg>
                        <span>{article.topics.length} Topic{article.topics.length === 1 ? '' : 's'}</span>
                      </div>
                    )}
                    {article.related_articles && article.related_articles.length > 0 && (
                      <div className="flex items-center gap-2">
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                        </svg>
                        <span>{article.related_articles.length} Related Article{article.related_articles.length === 1 ? '' : 's'}</span>
                      </div>
                    )}
                    {article.updated_at && article.updated_at !== article.created_at && (
                      <div className="flex items-center gap-2">
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span>Updated: {new Date(article.updated_at).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </header>
            
            {/* Article Content */}
            <div className="article-content space-y-6">
              {formatContent(article.content).map((paragraph, index) => {
                // Check if paragraph is a heading (starts with # or is short and bold-like)
                const isHeading = paragraph.length < 100 && (
                  paragraph.startsWith('#') || 
                  paragraph.toUpperCase() === paragraph ||
                  /^[A-Z][^.!?]*:$/.test(paragraph)
                )
                
                if (isHeading && paragraph.length < 100) {
                  return (
                    <h2 key={`para-${index}-${paragraph.substring(0, 20)}`} className="text-2xl font-bold mt-8 mb-4 text-black dark:text-white">
                      {paragraph.replace(/^#+\s*/, '')}
                    </h2>
                  )
                }
                
                return (
                  <p 
                    key={`para-${index}-${paragraph.substring(0, 20)}`} 
                    className="text-lg leading-8 text-gray-700 dark:text-gray-300 font-normal"
                    style={{ textAlign: 'justify' }}
                  >
                    {paragraph}
                  </p>
                )
              })}
            </div>

            {/* Additional Images */}
            {article.images && article.images.length > 1 && (
              <div className="my-12">
                <h2 className="text-3xl font-bold mb-6 text-black dark:text-white">Additional Images</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {article.images.slice(1).map((imageUrl, index) => (
                    <a
                      key={`img-${index}-${imageUrl.substring(0, 20)}`}
                      href={imageUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-200 block"
                      aria-label={`View ${index + 2} in full size`}
                    >
                      <img
                        src={imageUrl}
                        alt={`${article.title} - ${index + 2}`}
                        className="w-full h-auto object-cover hover:scale-105 transition-transform duration-200"
                        loading="lazy"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement
                          target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23ddd" width="400" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em" font-size="16"%3EImage not available%3C/text%3E%3C/svg%3E'
                          target.className = 'w-full h-auto object-cover opacity-50'
                        }}
                      />
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Related Articles */}
            {article.related_articles && article.related_articles.length > 0 && (
              <div className="mt-16 pt-8 border-t-2 border-gray-200 dark:border-gray-800">
                <h2 className="text-3xl font-bold mb-6 text-black dark:text-white">Related Articles</h2>
                <div className="space-y-4">
                  {article.related_articles.map((related, index) => (
                    <div 
                      key={`related-${index}-${related.id}`} 
                      className="bg-gray-50 dark:bg-gray-900 p-5 rounded-lg border border-gray-200 dark:border-gray-800 hover:shadow-md transition-shadow"
                    >
                      <Link
                        to={`/article/${related.id}`}
                        className="block hover:opacity-90 transition-opacity"
                      >
                        <h3 className="font-semibold text-lg text-black dark:text-white mb-2 hover:text-blue-600 dark:hover:text-blue-400">
                          {related.title}
                        </h3>
                        <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-500">
                          <time dateTime={related.created_at}>
                            {new Date(related.created_at).toLocaleDateString('en-US', { 
                              year: 'numeric', 
                              month: 'long', 
                              day: 'numeric'
                            })}
                          </time>
                          {related.similarity && (
                            <>
                              <span className="text-gray-300 dark:text-gray-700">•</span>
                              <span className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded text-xs">
                                {(related.similarity * 100).toFixed(0)}% similar
                              </span>
                            </>
                          )}
                        </div>
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sources */}
            {article.sources && article.sources.length > 0 && (
              <div className="mt-16 pt-8 border-t-2 border-gray-200 dark:border-gray-800">
                <h2 className="text-3xl font-bold mb-6 text-black dark:text-white">Sources</h2>
                <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg border border-gray-200 dark:border-gray-800">
                  <ul className="space-y-3">
                    {article.sources.map((source, index) => (
                      <li key={`source-${index}-${source.url}`} className="flex items-start gap-3">
                        <span className="text-gray-400 dark:text-gray-600 mt-1">•</span>
                        <div className="flex-1">
                          <span className="font-semibold text-gray-700 dark:text-gray-300">{source.name}</span>
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block text-blue-600 dark:text-blue-400 hover:underline text-sm mt-1 break-all"
                          >
                            {source.url}
                          </a>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
        </article>
        )}
      </main>
    </div>
  )
}
