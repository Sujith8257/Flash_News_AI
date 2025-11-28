import { Link } from "react-router-dom"
import { useState, useEffect } from "react"
import { fetchArticlesFromSupabase, isSupabaseConfigured, type Article } from "../lib/supabase"

export function Feed() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
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
        setArticles(supabaseArticles)
        
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

  // Get first paragraph as description
  const getDescription = (content: string) => {
    if (!content) return "No description available"
    const firstParagraph = content.split('\n\n')[0] || content.split('\n')[0]
    return firstParagraph.length > 150 ? firstParagraph.substring(0, 150) + '...' : firstParagraph
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
          <h2 className="px-4 text-3xl font-bold">News Feed</h2>
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
                      <p className="text-lg font-bold">{article.title}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {getDescription(article.content)}
                      </p>
                      {article.created_at && (
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                          Published: {formatDate(article.created_at)}
                        </p>
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
                    <div className="aspect-video w-full flex-shrink-0 rounded-lg overflow-hidden sm:w-64">
                      <img
                        src={article.images[0]}
                        alt={article.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          // Fallback to placeholder if image fails to load
                          const target = e.target as HTMLImageElement
                          target.style.display = 'none'
                          if (target.parentElement) {
                            target.parentElement.className = 'aspect-video w-full flex-shrink-0 rounded-lg bg-gray-100 dark:bg-gray-900 sm:w-64 flex items-center justify-center'
                          }
                        }}
                      />
                    </div>
                  ) : (
                    <div className="aspect-video w-full flex-shrink-0 rounded-lg bg-gray-100 dark:bg-gray-900 sm:w-64 flex items-center justify-center">
                      <svg className="h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                      </svg>
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
