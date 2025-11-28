import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"

export function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow">
        <section className="relative py-24 md:py-40 flex items-center justify-center text-center text-white overflow-hidden bg-gradient-to-b from-gray-900 to-black">
          <div className="relative z-10 container mx-auto px-4">
            <h1 className="text-5xl md:text-7xl font-extrabold mb-4">Flash News AI</h1>
            <p className="text-xl md:text-2xl max-w-3xl mx-auto mb-8 text-gray-300">
              Your real‑time, AI‑powered news feed. We summarize top stories, prioritize what
              matters to you, and keep you up to speed with instant updates.
            </p>
            <Button size="lg" asChild>
              <Link to="/feed">Get Started</Link>
            </Button>
          </div>
        </section>

        <section id="features" className="py-20 md:py-28">
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
            <div className="grid md:grid-cols-3 gap-8">
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-6">
                    <svg
                      fill="currentColor"
                      height="32"
                      viewBox="0 0 256 256"
                      width="32"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M200,48H136V16a8,8,0,0,0-16,0V48H56A32,32,0,0,0,24,80V192a32,32,0,0,0,32,32H200a32,32,0,0,0,32-32V80A32,32,0,0,0,200,48Zm16,144a16,16,0,0,1-16,16H56a16,16,0,0,1-16-16V80A16,16,0,0,1,56,64H200a16,16,0,0,1,16,16Zm-52-56H92a28,28,0,0,0,0,56h72a28,28,0,0,0,0-56Zm-28,16v24H120V152ZM80,164a12,12,0,0,1,12-12h12v24H92A12,12,0,0,1,80,164Zm84,12H152V152h12a12,12,0,0,1,0,24ZM72,108a12,12,0,1,1,12,12A12,12,0,0,1,72,108Zm88,0a12,12,0,1,1,12,12A12,12,0,0,1,160,108Z"></path>
                    </svg>
                  </div>
                  <CardTitle>AI summaries for every story</CardTitle>
                  <CardDescription>
                    We condense long articles into crisp highlights so you grasp the key points
                    in seconds—open the full piece only when you want more.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-6">
                    <svg
                      fill="currentColor"
                      height="32"
                      viewBox="0 0 256 256"
                      width="32"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M80,64a8,8,0,0,1,8-8H216a8,8,0,0,1,0,16H88A8,8,0,0,1,80,64Zm136,56H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16Zm0,64H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16ZM44,52A12,12,0,1,0,56,64,12,12,0,0,0,44,52Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,116Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,180Z"></path>
                    </svg>
                  </div>
                  <CardTitle>Personalized feed</CardTitle>
                  <CardDescription>
                    Follow topics, sources, and keywords. Your feed learns what you read and ranks
                    the most relevant stories first.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-6">
                    <svg
                      fill="currentColor"
                      height="32"
                      viewBox="0 0 256 256"
                      width="32"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm64-88a8,8,0,0,1-8,8H128a8,8,0,0,1-8-8V72a8,8,0,0,1,16,0v48h48A8,8,0,0,1,192,128Z"></path>
                    </svg>
                  </div>
                  <CardTitle>Real-time alerts</CardTitle>
                  <CardDescription>
                    Get instant updates as stories develop and track evolving events without
                    refreshing your page.
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </div>
        </section>

        <section id="pricing" className="bg-muted py-20 md:py-28">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-4xl md:text-5xl font-bold max-w-3xl mx-auto mb-4">
              Start reading in seconds
            </h2>
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
              See your personalized feed and AI summaries—no setup required.
            </p>
            <Button size="lg" asChild>
              <Link to="/feed">View Feed</Link>
            </Button>
          </div>
        </section>

        <section id="about" className="py-20 md:py-28">
          <div className="container mx-auto px-4">
            <div className="text-center max-w-3xl mx-auto mb-12">
              <h2 className="text-4xl md:text-5xl font-bold mb-4">About</h2>
              <p className="text-lg md:text-xl text-muted-foreground">
                Flash News AI is built by a small team focused on clarity, speed, and trustworthy
                news summaries.
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-8 mb-12">
              <Card>
                <CardHeader>
                  <CardTitle>Mission</CardTitle>
                  <CardDescription>
                    Deliver the fastest way to understand the news by combining high‑quality
                    sources with AI summaries.
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Values</CardTitle>
                  <CardDescription>
                    Respect time, reduce noise, and earn trust with accurate, readable updates.
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>What's next</CardTitle>
                  <CardDescription>
                    Topic following, smarter notifications, and collaborative reading tools.
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
            <div className="max-w-5xl mx-auto">
              <h3 className="text-2xl font-bold mb-6 text-center">Developers</h3>
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              </div>
            </div>
            <div className="mt-12 text-center">
              <Button size="lg" asChild>
                <Link to="/feed">View Feed</Link>
              </Button>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}

