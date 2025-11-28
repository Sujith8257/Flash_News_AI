import { Link, useParams } from "react-router-dom"
import { useState, useEffect } from "react"

interface Source {
  name: string
  url: string
}

interface ArticleData {
  id?: string
  title: string
  content: string
  sources: Source[]
  full_text?: string
  created_at?: string
}

export function Article() {
  const { id } = useParams<{ id?: string }>()
  const [article, setArticle] = useState<ArticleData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchArticle = async () => {
    try {
      setLoading(true)
      setError(null)
      
      let url = 'http://localhost:5000/api/article'
      if (id) {
        url = `http://localhost:5000/api/article/${id}`
      }
      
      const response = await fetch(url)
      const data = await response.json()
      
      if (data.success && data.article) {
        setArticle(data.article)
      } else {
        setError("No article found.")
      }
    } catch (err) {
      setError("Failed to fetch article. Make sure the API server is running.")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchArticle()
  }, [id])

  // Format content into paragraphs
  const formatContent = (content: string) => {
    if (!content) return []
    return content.split('\n\n').filter(p => p.trim().length > 0)
  }

  return (
    <div className="relative flex min-h-screen w-full flex-col bg-white dark:bg-black text-black dark:text-white">
      <main className="mx-auto w-full max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
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
          <article className="prose prose-lg dark:prose-invert max-w-none">
            <div className="mb-4">
              <h1 className="text-4xl font-bold mb-2">{article.title}</h1>
              {article.created_at && (
                <p className="text-sm text-gray-500 dark:text-gray-500">
                  Published: {new Date(article.created_at).toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              )}
            </div>
            
            {formatContent(article.content).map((paragraph, index) => (
              <p key={`para-${index}-${paragraph.substring(0, 20)}`} className="text-lg leading-relaxed text-gray-600 dark:text-gray-400 mb-4">
                {paragraph}
              </p>
            ))}

            {article.sources && article.sources.length > 0 && (
              <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-800">
                <h2 className="text-2xl font-bold mb-4">Sources</h2>
                <ul className="space-y-2">
                  {article.sources.map((source, index) => (
                    <li key={`source-${index}-${source.url}`} className="text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-semibold">Source: </span>
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        {source.name} - {source.url}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </article>
        )}
      </main>
    </div>
  )
}
