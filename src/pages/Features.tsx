import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"

export function Features() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow">
        <section className="py-16 md:py-24">
          <div className="container mx-auto px-4">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">Features</h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl">
              Everything you need to scan headlines quickly, dive deeper when needed, and stay
              current without the noise.
            </p>

            <div className="grid md:grid-cols-3 gap-8 mt-12">
              <Card>
                <CardHeader>
                  <CardTitle>AI Summaries</CardTitle>
                  <CardDescription>
                    Concise highlights for every article—understand the story at a glance and
                    decide what to read in full.
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Personalized Feed</CardTitle>
                  <CardDescription>
                    Follow topics and sources you care about. The feed learns your preferences and
                    surfaces the most relevant stories.
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Real-time Alerts</CardTitle>
                  <CardDescription>
                    Breaking updates appear instantly as stories evolve—no refresh required.
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Source Controls</CardTitle>
                  <CardDescription>
                    Tune your feed by source, region, and language to match your interests.
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Saved Articles</CardTitle>
                  <CardDescription>
                    Bookmark must‑reads and come back anytime—your list syncs across sessions.
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Clean Reading</CardTitle>
                  <CardDescription>
                    A distraction‑free layout with dark mode for comfortable reading day and night.
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}

