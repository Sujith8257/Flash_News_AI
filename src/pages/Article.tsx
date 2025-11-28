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
              <div className="mb-10 rounded-xl overflow-hidden shadow-lg">
                <img
                  src={article.images[0]}
                  alt={article.title}
                  className="w-full h-auto object-cover"
                  onError={(e) => {
                    // Hide image if it fails to load
                    const target = e.target as HTMLImageElement
                    target.style.display = 'none'
                  }}
                />
              </div>
            )}

            {/* Article Header */}
            <header className="mb-8 pb-6 border-b border-gray-200 dark:border-gray-800">
              <h1 className="text-5xl font-bold mb-4 text-black dark:text-white leading-tight">
                {article.title}
              </h1>
              {article.created_at && (
                <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-500">
                  <time dateTime={article.created_at}>
                    {new Date(article.created_at).toLocaleDateString('en-US', { 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </time>
                  <span className="text-gray-300 dark:text-gray-700">•</span>
                  <span>Flash News AI</span>
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
                <h3 className="text-xl font-semibold mb-4 text-black dark:text-white">Additional Images</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {article.images.slice(1).map((imageUrl, index) => (
                    <div key={`img-${index}-${imageUrl.substring(0, 20)}`} className="rounded-xl overflow-hidden shadow-md">
                      <img
                        src={imageUrl}
                        alt={`${article.title} - ${index + 2}`}
                        className="w-full h-auto object-cover"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement
                          target.style.display = 'none'
                        }}
                      />
                    </div>
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
