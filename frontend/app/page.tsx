import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="text-2xl font-bold text-primary">Transl8</div>
          <div className="flex items-center gap-4">
            <Link href="/sign-in">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/sign-up">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="mb-6 text-5xl font-bold tracking-tight">
          AI-Powered Translation for
          <span className="text-primary"> Software & Technical Content</span>
        </h1>
        <p className="mx-auto mb-8 max-w-2xl text-xl text-gray-600">
          Professional translation platform designed for software localization, product labels,
          and technical documentation. API-first, self-serve, and transparent pricing.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link href="/sign-up">
            <Button size="lg">Start Free Trial</Button>
          </Link>
          <Link href="#features">
            <Button variant="outline" size="lg">
              Learn More
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <h2 className="mb-12 text-center text-3xl font-bold">Why Choose Transl8?</h2>
        <div className="grid gap-6 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Structured Content Expert</CardTitle>
              <CardDescription>
                XML, XLIFF, JSON handling with perfect structure preservation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>✓ Android XML & iOS .strings</li>
                <li>✓ XLIFF 1.2 & 2.0 support</li>
                <li>✓ Nested JSON with placeholder detection</li>
                <li>✓ CSV & XLSX bulk translation</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>API-First Design</CardTitle>
              <CardDescription>
                Built for integration with your PIM, CMS, or development workflow
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>✓ RESTful API with OpenAPI docs</li>
                <li>✓ Webhooks for automation</li>
                <li>✓ PIM connector support</li>
                <li>✓ CLI tools for developers</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Professional Features</CardTitle>
              <CardDescription>
                Translation Memory, glossaries, and quality checks built-in
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>✓ Translation Memory reuse</li>
                <li>✓ Custom glossaries per project</li>
                <li>✓ Automated QA checks</li>
                <li>✓ Team collaboration tools</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Use Cases */}
      <section className="bg-white py-20">
        <div className="container mx-auto px-4">
          <h2 className="mb-12 text-center text-3xl font-bold">Perfect For</h2>
          <div className="grid gap-8 md:grid-cols-3">
            <div className="text-center">
              <div className="mb-4 text-4xl">💻</div>
              <h3 className="mb-2 text-xl font-semibold">Software Localization</h3>
              <p className="text-gray-600">
                Translate app interfaces, mobile apps, and web applications with context preservation
              </p>
            </div>
            <div className="text-center">
              <div className="mb-4 text-4xl">🏷️</div>
              <h3 className="mb-2 text-xl font-semibold">Product Information</h3>
              <p className="text-gray-600">
                Scale product labels, descriptions, and catalogs for global e-commerce
              </p>
            </div>
            <div className="text-center">
              <div className="mb-4 text-4xl">📄</div>
              <h3 className="mb-2 text-xl font-semibold">Technical Docs</h3>
              <p className="text-gray-600">
                Translate manuals, compliance documents, and technical specifications
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h2 className="mb-6 text-4xl font-bold">Ready to Get Started?</h2>
        <p className="mb-8 text-xl text-gray-600">
          Join companies using Transl8 to scale their global content
        </p>
        <Link href="/sign-up">
          <Button size="lg">Start Your Free Trial</Button>
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t bg-gray-50 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-gray-600">
          <p>© 2025 Transl8. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
