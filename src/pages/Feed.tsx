import { Link } from "react-router-dom"
import { useState, useEffect } from "react"
import { fetchArticlesFromSupabase, isSupabaseConfigured, type Article } from "../lib/supabase"

export function Feed() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Set page title
    document.title = "News Feed - Flash News AI"
    
    const fetchArticles = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Check if Supabase is configured
        if (!isSupabaseConfigured()) {
          setError("Supabase is not configured. Please add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to your .env file.")
          return
        }
        
        // Fetch articles directly from Supabase
        const supabaseArticles = await fetchArticlesFromSupabase()
        
        // Sort articles by created_at (newest first) as a safety measure
        // This ensures new articles always appear at the top
        const sortedArticles = [...supabaseArticles].sort((a, b) => {
          const dateA = new Date(a.created_at || 0).getTime()
          const dateB = new Date(b.created_at || 0).getTime()
          return dateB - dateA // Descending order (newest first)
        })
        
        setArticles(sortedArticles)
        
        if (supabaseArticles.length === 0) {
          setError("No articles found yet. Articles are generated automatically every 30 minutes.")
        }
      } catch (err) {
        setError("Failed to fetch articles from Supabase. Please check your connection and Supabase configuration.")
        console.error("Error fetching articles:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchArticles()
    
    // Refresh articles every 5 minutes
    const interval = setInterval(fetchArticles, 300000)
    return () => clearInterval(interval)
  }, [])

  // Get content preview (4-5 line summary) or fallback to first paragraph
  const getContentPreview = (article: Article) => {
    // Use content_preview if available (4-5 line summary)
    if (article.content_preview) {
      return article.content_preview
    }
    // Fallback: use first paragraph if content_preview not available
    if (article.content) {
      const firstParagraph = article.content.split('\n\n')[0] || article.content.split('\n')[0]
      return firstParagraph.length > 200 ? firstParagraph.substring(0, 200) + '...' : firstParagraph
    }
    return "No preview available"
  }

  // Format date
  const formatDate = (dateString?: string) => {
    if (!dateString) return ""
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return ""
    }
  }

  // Check if article is new (within last 24 hours)
  const isNewArticle = (dateString?: string) => {
    if (!dateString) return false
    try {
      const articleDate = new Date(dateString)
      const now = new Date()
      const hoursDiff = (now.getTime() - articleDate.getTime()) / (1000 * 60 * 60)
      return hoursDiff <= 24
    } catch {
      return false
    }
  }

  return (
    <div className="flex min-h-screen w-full flex-col bg-white dark:bg-black text-black dark:text-white">
      <header className="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex items-center gap-4">
          <Link to="/feed">
            <img src="/logo1.png" alt="Flash News AI logo" className="h-12 w-12 object-contain" />
          </Link>
          <Link to="/" className="text-xl font-bold">
            Flash News AI
          </Link>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative hidden sm:block">
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-500 dark:text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              className="w-full rounded-full border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 py-2 pl-10 pr-4 text-base focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white"
              placeholder="Search"
            />
          </div>
        </div>
      </header>
      <main className="flex-1">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-extrabold mb-2 text-black dark:text-white">News Feed</h1>
            <p className="text-gray-600 dark:text-gray-400 text-lg">Stay updated with the latest global events</p>
          </div>
          <div className="mt-6 space-y-8">
            {loading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <svg className="animate-spin h-8 w-8 mx-auto mb-4 text-gray-600 dark:text-gray-400" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p className="text-gray-600 dark:text-gray-400">Loading articles...</p>
                </div>
              </div>
            )}

            {error && !loading && (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <p className="text-yellow-800 dark:text-yellow-200">{error}</p>
              </div>
            )}

            {!loading && articles.length === 0 && !error && (
              <div className="text-center py-12">
                <p className="text-gray-600 dark:text-gray-400">No articles available yet. Articles are generated automatically every 30 minutes.</p>
              </div>
            )}

            {articles.map((article) => (
              <div key={article.id || article.title} className="border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-black hover:shadow-lg transition-shadow">
                <div className="flex flex-col gap-4 p-4 sm:flex-row">
                  <div className="flex flex-1 flex-col gap-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <p className="text-lg font-bold">{article.title}</p>
                        {isNewArticle(article.created_at) && (
                          <span className="px-2 py-0.5 text-xs font-semibold bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full">
                            NEW
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                        {getContentPreview(article)}
                      </p>
                      {article.created_at && (
                        <div className="flex flex-wrap items-center gap-3 mt-2">
                          <p className="text-xs text-gray-500 dark:text-gray-500">
                            Generated: {formatDate(article.created_at)}
                          </p>
                          {article.sources && article.sources.length > 0 && (
                            <span className="text-xs text-gray-400 dark:text-gray-600">
                              • {article.sources.length} source{article.sources.length === 1 ? '' : 's'}
                            </span>
                          )}
                          {article.images && article.images.length > 0 && (
                            <span className="text-xs text-gray-400 dark:text-gray-600">
                              • {article.images.length} image{article.images.length === 1 ? '' : 's'}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <Link
                      to={`/article/${article.id || ''}`}
                      className="inline-flex items-center justify-center gap-2 w-fit px-4 py-2 text-sm font-medium text-white bg-black dark:bg-white dark:text-black rounded-full hover:bg-gray-900 dark:hover:bg-gray-100 transition-colors"
                    >
                      <span>Read Article</span>
                      <svg
                        className="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </Link>
                  </div>
                  {article.images && article.images.length > 0 ? (
                    <a 
                      href={article.images[0]} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="aspect-video w-full flex-shrink-0 rounded-lg overflow-hidden sm:w-64 shadow-md hover:shadow-lg transition-shadow block"
                      aria-label="View article image in full size"
                    >
                      <img
                        src={article.images[0]}
                        alt={article.title}
                        className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                        loading="lazy"
                        onError={(e) => {
                          // Fallback to placeholder if image fails to load
                          const target = e.target as HTMLImageElement
                          target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23ddd" width="400" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em" font-size="14"%3EImage not available%3C/text%3E%3C/svg%3E'
                          target.className = 'w-full h-full object-cover opacity-50'
                        }}
                      />
                    </a>
                  ) : (
                    <div className="aspect-video w-full flex-shrink-0 rounded-lg bg-gray-100 dark:bg-gray-900 sm:w-64 flex items-center justify-center border-2 border-dashed border-gray-300 dark:border-gray-700">
                      <div className="text-center">
                        <svg className="h-12 w-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <p className="text-xs text-gray-400">No image</p>
                      </div>
                    </div>
                  )}
                </div>
                {article.sources && article.sources.length > 0 && (
                  <div className="border-t border-gray-200 dark:border-gray-800 px-4 py-2">
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      Sources: {article.sources.map(s => s.name).join(', ')}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
