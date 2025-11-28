import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"

export function About() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow">
        <section className="py-16 md:py-24">
          <div className="container mx-auto px-4">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">About Flash News AI</h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl">
              Flash News AI is a lightweight news reader that uses AI to summarize and prioritize
              stories in a fast, distraction‑free feed.
            </p>

            <div className="mt-12">
              <h2 className="text-2xl font-bold mb-4">Developers</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>TANGUTURI VENKATA SUJITH GOPI</li>
                <li>DAGGUPATI SATHWIK CHOWDARY</li>
                <li>GANIPINENI BHARDWAJ NAIDU</li>
                <li>BIREDDY GOWTHAM</li>
              </ul>
            </div>

            <div className="mt-12 grid md:grid-cols-3 gap-8">
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
                    Clarity, speed, and trust. We prioritize accuracy and a clean reading
                    experience.
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Contact</CardTitle>
                  <CardDescription>
                    Questions or feedback? Reach out via the Contact link in the footer.
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

