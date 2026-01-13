import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { 
  Sparkles, 
  Zap, 
  Shield, 
  Clock, 
  TrendingUp, 
  CheckCircle2,
  ArrowRight,
  Newspaper,
  Brain,
  Search,
  Globe
} from "lucide-react"
import { useEffect, useState } from "react"
import { getArticleCount, getRecentArticles, type Article } from "@/lib/supabase"

export function Home() {
  const [articleCount, setArticleCount] = useState(0)
  const [realArticleCount, setRealArticleCount] = useState(0)
  const [recentArticles, setRecentArticles] = useState<Article[]>([])
  const [isVisible, setIsVisible] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    setIsVisible(true)
    
    // Fetch real data
    const fetchData = async () => {
      try {
        const count = await getArticleCount()
        setRealArticleCount(count)
        
        const articles = await getRecentArticles(3)
        setRecentArticles(articles)
        
        // Animate counter to real value
        const target = count
        const duration = 2000
        const steps = 60
        const increment = target / steps
        let current = 0
        const timer = setInterval(() => {
          current += increment
          if (current >= target) {
            setArticleCount(target)
            clearInterval(timer)
            setIsLoading(false)
          } else {
            setArticleCount(Math.floor(current))
          }
        }, duration / steps)
      } catch (error) {
        console.error('Error fetching data:', error)
        setIsLoading(false)
      }
    }
    
    fetchData()
  }, [])

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow">
        {/* Enhanced Hero Section */}
        <section className="relative py-24 md:py-40 flex items-center justify-center text-center text-white overflow-hidden bg-gradient-to-br from-gray-900 via-black to-gray-900">
          {/* Animated background elements */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          </div>
          
          <div className={`relative z-10 container mx-auto px-4 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 mb-6">
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-medium">AI-Powered News Aggregation</span>
            </div>
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-extrabold mb-6 bg-gradient-to-r from-white via-gray-200 to-white bg-clip-text text-transparent animate-gradient">
              Flash News AI
            </h1>
            <p className="text-xl md:text-2xl lg:text-3xl max-w-4xl mx-auto mb-4 text-gray-300 font-light">
              Your real‑time, AI‑powered news feed
            </p>
            <p className="text-lg md:text-xl max-w-2xl mx-auto mb-10 text-gray-400">
              We summarize top stories, verify facts, and keep you up to speed with instant updates from multiple trusted sources.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button size="lg" className="text-lg px-8 py-6 group" asChild>
                <Link to="/feed">
                  Get Started
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-6 border-white/20 text-white hover:bg-white/10" asChild>
                <Link to="/features">Learn More</Link>
              </Button>
            </div>
          </div>
        </section>

        {/* Statistics Section */}
        <section className="py-16 md:py-24 bg-muted/50 border-y">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold mb-2">
                  {isLoading ? articleCount.toLocaleString() : realArticleCount.toLocaleString()}
                  {!isLoading && realArticleCount > 0 && '+'}
                </div>
                <div className="text-muted-foreground">Articles Generated</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold mb-2">6+</div>
                <div className="text-muted-foreground">News Sources</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold mb-2">30min</div>
                <div className="text-muted-foreground">Update Frequency</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold mb-2">24/7</div>
                <div className="text-muted-foreground">Automated</div>
              </div>
            </div>
          </div>
        </section>

        {/* Featured Articles Section */}
        {isLoading ? (
          <section className="py-20 md:py-28 bg-background">
            <div className="container mx-auto px-4">
              <div className="text-center max-w-3xl mx-auto mb-12">
                <h2 className="text-4xl md:text-5xl font-bold mb-4">
                  Latest Articles
                </h2>
                <p className="text-lg md:text-xl text-muted-foreground">
                  Loading articles...
                </p>
              </div>
            </div>
          </section>
        ) : recentArticles.length > 0 ? (
          <section className="py-20 md:py-28 bg-background">
            <div className="container mx-auto px-4">
              <div className="text-center max-w-3xl mx-auto mb-12">
                <h2 className="text-4xl md:text-5xl font-bold mb-4">
                  Latest Articles
                </h2>
                <p className="text-lg md:text-xl text-muted-foreground">
                  Fresh AI-generated news articles from our automated system
                </p>
              </div>
              <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                {recentArticles.map((article) => (
                  <Card 
                    key={article.id} 
                    className="hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-2 hover:border-primary/20 overflow-hidden"
                  >
                    {article.images && article.images.length > 0 && (
                      <div className="aspect-video w-full overflow-hidden bg-muted">
                        <img 
                          src={article.images[0]} 
                          alt={article.title}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none'
                          }}
                        />
                      </div>
                    )}
                    <CardHeader>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                        <Clock className="w-3 h-3" />
                        <span>
                          {new Date(article.created_at).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                      <CardTitle className="text-xl mb-3 line-clamp-2 min-h-[3.5rem]">
                        {article.title}
                      </CardTitle>
                      <CardDescription className="text-sm line-clamp-3 min-h-[4.5rem]">
                        {article.content_preview || (article.content ? article.content.substring(0, 150) + '...' : 'No preview available')}
                      </CardDescription>
                      {article.sources && article.sources.length > 0 && (
                        <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
                          <Globe className="w-3 h-3" />
                          <span>{article.sources.length} source{article.sources.length > 1 ? 's' : ''}</span>
                        </div>
                      )}
                    </CardHeader>
                    <div className="px-6 pb-6">
                      <Button variant="outline" className="w-full" asChild>
                        <Link to={`/article/${article.id}`}>
                          Read More
                          <ArrowRight className="ml-2 w-4 h-4" />
                        </Link>
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
              <div className="text-center mt-12">
                <Button size="lg" className="text-lg px-8 py-6 group" asChild>
                  <Link to="/feed">
                    View All Articles
                    <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </Button>
              </div>
            </div>
          </section>
        ) : (
          <section className="py-20 md:py-28 bg-background">
            <div className="container mx-auto px-4">
              <div className="text-center max-w-3xl mx-auto">
                <h2 className="text-4xl md:text-5xl font-bold mb-4">
                  Latest Articles
                </h2>
                <p className="text-lg md:text-xl text-muted-foreground mb-8">
                  No articles yet. Check back soon for AI-generated news!
                </p>
                <Button size="lg" className="text-lg px-8 py-6 group" asChild>
                  <Link to="/feed">
                    View Feed
                    <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </Button>
              </div>
            </div>
          </section>
        )}

        {/* How It Works Section */}
        <section className="py-20 md:py-28 bg-background">
          <div className="container mx-auto px-4">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-4xl md:text-5xl font-bold mb-4">
                How It Works
              </h2>
              <p className="text-lg md:text-xl text-muted-foreground">
                Our AI-powered system aggregates, verifies, and generates news articles automatically
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              <div className="text-center">
                <div className="flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 text-primary mb-6 mx-auto">
                  <Search className="w-10 h-10" />
                </div>
                <h3 className="text-2xl font-bold mb-3">1. Aggregate</h3>
                <p className="text-muted-foreground">
                  Collects news from 6+ trusted sources including NewsAPI, GDELT, Google News, BBC, and Reddit
                </p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 text-primary mb-6 mx-auto">
                  <Shield className="w-10 h-10" />
                </div>
                <h3 className="text-2xl font-bold mb-3">2. Verify</h3>
                <p className="text-muted-foreground">
                  AI agents cross-reference information across sources to verify facts and ensure accuracy
                </p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 text-primary mb-6 mx-auto">
                  <Brain className="w-10 h-10" />
                </div>
                <h3 className="text-2xl font-bold mb-3">3. Generate</h3>
                <p className="text-muted-foreground">
                  Creates comprehensive, well-structured articles with proper citations and source attribution
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Enhanced Features Section */}
        <section id="features" className="py-20 md:py-28 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-4xl md:text-5xl font-bold mb-4">
                Built for fast, focused reading
              </h2>
              <p className="text-lg md:text-xl text-muted-foreground">
                Flash News AI blends powerful summarization with a clean feed so you see more
                signal and less noise.
              </p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <Card className="hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-2 hover:border-primary/20">
                <CardHeader>
                  <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-6">
                    <Brain className="w-8 h-8" />
                  </div>
                  <CardTitle className="text-2xl mb-3">AI Summaries</CardTitle>
                  <CardDescription className="text-base">
                    We condense long articles into crisp highlights so you grasp the key points
                    in seconds—open the full piece only when you want more.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card className="hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-2 hover:border-primary/20">
                <CardHeader>
                  <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-6">
                    <Shield className="w-8 h-8" />
                  </div>
                  <CardTitle className="text-2xl mb-3">Fact-Checked</CardTitle>
                  <CardDescription className="text-base">
                    Every article is verified by AI agents that cross-reference information across
                    multiple sources to ensure accuracy and reliability.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card className="hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-2 hover:border-primary/20">
                <CardHeader>
                  <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-6">
                    <Clock className="w-8 h-8" />
                  </div>
                  <CardTitle className="text-2xl mb-3">Real-Time Updates</CardTitle>
                  <CardDescription className="text-base">
                    Get instant updates as stories develop. New articles are generated every 30 minutes
                    automatically, keeping you informed around the clock.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card className="hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-2 hover:border-primary/20">
                <CardHeader>
                  <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-6">
                    <Globe className="w-8 h-8" />
                  </div>
                  <CardTitle className="text-2xl mb-3">Multi-Source</CardTitle>
                  <CardDescription className="text-base">
                    Aggregates news from 6+ trusted sources including NewsAPI, GDELT, Google News,
                    BBC, Reddit, and more for comprehensive coverage.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card className="hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-2 hover:border-primary/20">
                <CardHeader>
                  <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-6">
                    <Zap className="w-8 h-8" />
                  </div>
                  <CardTitle className="text-2xl mb-3">Lightning Fast</CardTitle>
                  <CardDescription className="text-base">
                    Optimized for speed with instant loading, smart caching, and efficient data
                    processing for the best reading experience.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card className="hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-2 hover:border-primary/20">
                <CardHeader>
                  <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-6">
                    <Newspaper className="w-8 h-8" />
                  </div>
                  <CardTitle className="text-2xl mb-3">Well-Structured</CardTitle>
                  <CardDescription className="text-base">
                    Every article includes proper formatting, images, source citations, and
                    related articles for comprehensive coverage.
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </div>
        </section>

        {/* Enhanced CTA Section */}
        <section className="relative py-20 md:py-32 overflow-hidden bg-gradient-to-br from-background via-muted/50 to-background">
          <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
          <div className="container mx-auto px-4 text-center relative z-10">
            <div className="max-w-3xl mx-auto">
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
                Start reading in seconds
              </h2>
              <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
                See your personalized feed and AI summaries—no setup required. 
                Get instant access to verified, comprehensive news articles.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
                <Button size="lg" className="text-lg px-8 py-6 group" asChild>
                  <Link to="/feed">
                    View Feed
                    <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" className="text-lg px-8 py-6" asChild>
                  <Link to="/about">Learn More</Link>
                </Button>
              </div>
              <div className="flex flex-wrap justify-center gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary" />
                  <span>No sign-up required</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary" />
                  <span>Free forever</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary" />
                  <span>AI-powered summaries</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary" />
                  <span>Fact-checked articles</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Enhanced About Section */}
        <section id="about" className="py-20 md:py-28 bg-background">
          <div className="container mx-auto px-4">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-4xl md:text-5xl font-bold mb-4">About Flash News AI</h2>
              <p className="text-lg md:text-xl text-muted-foreground">
                Built with cutting-edge AI technology to deliver clarity, speed, and trustworthy
                news summaries. We're on a mission to make news consumption faster and more reliable.
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-8 mb-16 max-w-5xl mx-auto">
              <Card className="hover:shadow-lg transition-all duration-300">
                <CardHeader>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                      <TrendingUp className="w-6 h-6 text-primary" />
                    </div>
                    <CardTitle className="text-xl">Mission</CardTitle>
                  </div>
                  <CardDescription className="text-base">
                    Deliver the fastest way to understand the news by combining high‑quality
                    sources with AI-powered summaries and fact-checking.
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card className="hover:shadow-lg transition-all duration-300">
                <CardHeader>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                      <Shield className="w-6 h-6 text-primary" />
                    </div>
                    <CardTitle className="text-xl">Values</CardTitle>
                  </div>
                  <CardDescription className="text-base">
                    Respect time, reduce noise, and earn trust with accurate, readable updates
                    backed by multiple verified sources.
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card className="hover:shadow-lg transition-all duration-300">
                <CardHeader>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                      <Sparkles className="w-6 h-6 text-primary" />
                    </div>
                    <CardTitle className="text-xl">What's Next</CardTitle>
                  </div>
                  <CardDescription className="text-base">
                    Topic following, smarter notifications, personalized recommendations,
                    and collaborative reading tools.
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
            
            {/* Technology Stack */}
            <div className="max-w-4xl mx-auto mb-12">
              <h3 className="text-2xl font-bold mb-8 text-center">Powered By</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <Card className="text-center p-6 hover:shadow-md transition-shadow">
                  <div className="text-2xl font-bold mb-2">CrewAI</div>
                  <div className="text-sm text-muted-foreground">Multi-Agent System</div>
                </Card>
                <Card className="text-center p-6 hover:shadow-md transition-shadow">
                  <div className="text-2xl font-bold mb-2">Gemini</div>
                  <div className="text-sm text-muted-foreground">Google AI</div>
                </Card>
                <Card className="text-center p-6 hover:shadow-md transition-shadow">
                  <div className="text-2xl font-bold mb-2">Supabase</div>
                  <div className="text-sm text-muted-foreground">Database</div>
                </Card>
                <Card className="text-center p-6 hover:shadow-md transition-shadow">
                  <div className="text-2xl font-bold mb-2">React</div>
                  <div className="text-sm text-muted-foreground">Frontend</div>
                </Card>
              </div>
            </div>

            <div className="text-center">
              <Button size="lg" className="text-lg px-8 py-6 group" asChild>
                <Link to="/feed">
                  Explore the Feed
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}

