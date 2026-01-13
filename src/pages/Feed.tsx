import { Link } from "react-router-dom"
import { useState, useEffect, useMemo } from "react"
import { fetchArticlesFromSupabase, isSupabaseConfigured, type Article } from "../lib/supabase"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { 
  Search, 
  Clock, 
  Globe, 
  Image as ImageIcon, 
  ArrowRight, 
  TrendingUp,
  Sparkles
} from "lucide-react"

export function Feed() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [sortBy, setSortBy] = useState<"newest" | "oldest">("newest")

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

  // Filter and sort articles
  const filteredAndSortedArticles = useMemo(() => {
    let filtered = [...articles]

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(article => 
        article.title?.toLowerCase().includes(query) ||
        article.content?.toLowerCase().includes(query) ||
        article.content_preview?.toLowerCase().includes(query) ||
        article.topics?.some(topic => topic.toLowerCase().includes(query)) ||
        article.sources?.some(source => source.name?.toLowerCase().includes(query))
      )
    }

    // Sort
    filtered.sort((a, b) => {
      const dateA = new Date(a.created_at || 0).getTime()
      const dateB = new Date(b.created_at || 0).getTime()
      return sortBy === "newest" ? dateB - dateA : dateA - dateB
    })

    return filtered
  }, [articles, searchQuery, sortBy])

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

  // Format relative time
  const getRelativeTime = (dateString?: string) => {
    if (!dateString) return ""
    try {
      const date = new Date(dateString)
      const now = new Date()
      const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
      
      if (diffInSeconds < 60) return "Just now"
      if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
      if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
      if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`
      return formatDate(dateString)
    } catch {
      return ""
    }
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="bg-gradient-to-br from-muted/50 to-background border-b py-12">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-6 h-6 text-primary" />
                <h1 className="text-4xl md:text-5xl font-extrabold">News Feed</h1>
              </div>
              <p className="text-lg text-muted-foreground mb-6">
                Stay updated with the latest AI-generated news articles
              </p>
              
              {/* Search and Filter Bar */}
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Search articles by title, content, topics, or sources..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 h-12 text-base"
                  />
                </div>
                <Button
                  variant="outline"
                  onClick={() => setSortBy(sortBy === "newest" ? "oldest" : "newest")}
                  className="h-12"
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  {sortBy === "newest" ? "Newest" : "Oldest"}
                </Button>
              </div>

              {/* Results Count */}
              {!loading && (
                <div className="mt-4 text-sm text-muted-foreground">
                  {filteredAndSortedArticles.length === articles.length ? (
                    <span>{articles.length} article{articles.length !== 1 ? 's' : ''} total</span>
                  ) : (
                    <span>
                      Showing {filteredAndSortedArticles.length} of {articles.length} article{articles.length !== 1 ? 's' : ''}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Articles Section */}
        <section className="py-8">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              {loading && (
                <div className="flex items-center justify-center py-20">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Loading articles...</p>
                  </div>
                </div>
              )}

              {error && !loading && (
                <Card className="border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20">
                  <CardContent className="pt-6">
                    <p className="text-yellow-800 dark:text-yellow-200">{error}</p>
                  </CardContent>
                </Card>
              )}

              {!loading && filteredAndSortedArticles.length === 0 && !error && (
                <Card>
                  <CardContent className="pt-12 pb-12 text-center">
                    <p className="text-muted-foreground text-lg mb-4">
                      {searchQuery ? "No articles found matching your search." : "No articles available yet."}
                    </p>
                    {searchQuery && (
                      <Button variant="outline" onClick={() => setSearchQuery("")}>
                        Clear Search
                      </Button>
                    )}
                  </CardContent>
                </Card>
              )}

              <div className="space-y-6">
                {filteredAndSortedArticles.map((article) => (
                  <Card 
                    key={article.id || article.title} 
                    className="hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-2"
                  >
                    <div className="flex flex-col md:flex-row gap-6 p-6">
                      {/* Content */}
                      <div className="flex-1 space-y-4">
                        <div className="space-y-2">
                          <div className="flex items-start justify-between gap-4">
                            <CardTitle className="text-2xl leading-tight pr-4">
                              {article.title}
                            </CardTitle>
                            {isNewArticle(article.created_at) && (
                              <span className="px-3 py-1 text-xs font-semibold bg-primary/10 text-primary rounded-full whitespace-nowrap">
                                NEW
                              </span>
                            )}
                          </div>
                          <CardDescription className="text-base leading-relaxed line-clamp-3">
                            {getContentPreview(article)}
                          </CardDescription>
                        </div>

                        {/* Metadata */}
                        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4" />
                            <span>{getRelativeTime(article.created_at)}</span>
                          </div>
                          {article.sources && article.sources.length > 0 && (
                            <div className="flex items-center gap-2">
                              <Globe className="w-4 h-4" />
                              <span>{article.sources.length} source{article.sources.length !== 1 ? 's' : ''}</span>
                            </div>
                          )}
                          {article.images && article.images.length > 0 && (
                            <div className="flex items-center gap-2">
                              <ImageIcon className="w-4 h-4" />
                              <span>{article.images.length} image{article.images.length !== 1 ? 's' : ''}</span>
                            </div>
                          )}
                          {article.topics && article.topics.length > 0 && (
                            <div className="flex flex-wrap gap-2">
                              {article.topics.slice(0, 3).map((topic, idx) => (
                                <span 
                                  key={idx}
                                  className="px-2 py-1 bg-muted rounded-md text-xs"
                                >
                                  {topic}
                                </span>
                              ))}
                              {article.topics.length > 3 && (
                                <span className="px-2 py-1 text-xs text-muted-foreground">
                                  +{article.topics.length - 3} more
                                </span>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-4">
                          <Button asChild>
                            <Link to={`/article/${article.id || ''}`}>
                              Read Full Article
                              <ArrowRight className="ml-2 w-4 h-4" />
                            </Link>
                          </Button>
                          {article.sources && article.sources.length > 0 && (
                            <div className="text-xs text-muted-foreground">
                              Sources: {article.sources.slice(0, 2).map(s => s.name).join(', ')}
                              {article.sources.length > 2 && ` +${article.sources.length - 2} more`}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Image */}
                      {article.images && article.images.length > 0 ? (
                        <div className="md:w-80 flex-shrink-0">
                          <div className="aspect-video w-full rounded-lg overflow-hidden bg-muted">
                            <img
                              src={article.images[0]}
                              alt={article.title}
                              className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                              loading="lazy"
                              onError={(e) => {
                                const target = e.target as HTMLImageElement
                                target.style.display = 'none'
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <div className="md:w-80 flex-shrink-0 aspect-video rounded-lg bg-muted flex items-center justify-center border-2 border-dashed">
                          <div className="text-center">
                            <ImageIcon className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                            <p className="text-xs text-muted-foreground">No image</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}
