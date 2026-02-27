import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'GEO Tool - SEO + AI Search Optimization',
  description: 'Optimize your content for Google Search AND AI engines like ChatGPT, Perplexity, and Claude',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              {/* Logo */}
              <a href="/" className="flex items-center gap-2">
                <span className="text-2xl">🎯</span>
                <span className="text-xl font-bold text-gray-900">GEO Tool</span>
              </a>
              
              {/* Navigation - Tools Dropdown */}
              <nav className="hidden md:flex items-center gap-1">
                <div className="relative group">
                  <button className="px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg flex items-center gap-1">
                    Tools
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {/* Dropdown */}
                  <div className="absolute top-full left-0 mt-1 w-64 bg-white rounded-xl shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                    <div className="p-2">
                      <a href="/" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50">
                        <span className="text-xl">📊</span>
                        <div>
                          <div className="font-medium text-gray-900">SEO + GEO Analyzer</div>
                          <div className="text-xs text-gray-500">Combined scoring for Google & AI</div>
                        </div>
                      </a>
                      <a href="/visibility" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50">
                        <span className="text-xl">🔍</span>
                        <div>
                          <div className="font-medium text-gray-900">AI Visibility Checker</div>
                          <div className="text-xs text-gray-500">Check robots.txt, sitemap, llms.txt</div>
                        </div>
                      </a>
                      <a href="/ssr" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50">
                        <span className="text-xl">⚡</span>
                        <div>
                          <div className="font-medium text-gray-900">SSR Checker</div>
                          <div className="text-xs text-gray-500">Check server-side rendering</div>
                        </div>
                      </a>
                      <a href="/article" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50">
                        <span className="text-xl">✍️</span>
                        <div>
                          <div className="font-medium text-gray-900">AI Article Generator</div>
                          <div className="text-xs text-gray-500">Generate GEO-optimized articles</div>
                        </div>
                      </a>
                      <a href="/rewriter" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50">
                        <span className="text-xl">🔄</span>
                        <div>
                          <div className="font-medium text-gray-900">Content Rewriter</div>
                          <div className="text-xs text-gray-500">Add stats, citations, quotes</div>
                        </div>
                      </a>
                      <a href="/faq" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50">
                        <span className="text-xl">❓</span>
                        <div>
                          <div className="font-medium text-gray-900">FAQ Generator</div>
                          <div className="text-xs text-gray-500">Generate FAQ + schema markup</div>
                        </div>
                      </a>
                    </div>
                  </div>
                </div>
                
                <a href="/article" className="px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
                  Article Generator
                </a>
                <a href="/visibility" className="px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
                  AI Visibility
                </a>
              </nav>

              {/* CTA Button */}
              <div className="flex items-center gap-3">
                <a 
                  href="/"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
                >
                  Get Started
                </a>
              </div>
            </div>
          </div>
          
          {/* Mobile Nav */}
          <div className="md:hidden border-t border-gray-200 px-4 py-2 flex gap-2 overflow-x-auto">
            <a href="/" className="px-3 py-1.5 text-sm bg-gray-100 rounded-lg whitespace-nowrap">Analyzer</a>
            <a href="/visibility" className="px-3 py-1.5 text-sm bg-gray-100 rounded-lg whitespace-nowrap">Visibility</a>
            <a href="/ssr" className="px-3 py-1.5 text-sm bg-gray-100 rounded-lg whitespace-nowrap">SSR</a>
            <a href="/article" className="px-3 py-1.5 text-sm bg-gray-100 rounded-lg whitespace-nowrap">Article</a>
            <a href="/rewriter" className="px-3 py-1.5 text-sm bg-gray-100 rounded-lg whitespace-nowrap">Rewriter</a>
            <a href="/faq" className="px-3 py-1.5 text-sm bg-gray-100 rounded-lg whitespace-nowrap">FAQ</a>
          </div>
        </header>
        
        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        
        {/* Footer */}
        <footer className="border-t border-gray-200 mt-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid md:grid-cols-4 gap-8">
              {/* Brand */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-2xl">🎯</span>
                  <span className="text-xl font-bold text-gray-900">GEO Tool</span>
                </div>
                <p className="text-sm text-gray-600">
                  Optimize your content for both Google Search and AI search engines.
                </p>
              </div>
              
              {/* Tools */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-4">Tools</h4>
                <ul className="space-y-2 text-sm">
                  <li><a href="/" className="text-gray-600 hover:text-gray-900">SEO + GEO Analyzer</a></li>
                  <li><a href="/visibility" className="text-gray-600 hover:text-gray-900">AI Visibility Checker</a></li>
                  <li><a href="/ssr" className="text-gray-600 hover:text-gray-900">SSR Checker</a></li>
                  <li><a href="/article" className="text-gray-600 hover:text-gray-900">AI Article Generator</a></li>
                </ul>
              </div>
              
              {/* More Tools */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-4">More Tools</h4>
                <ul className="space-y-2 text-sm">
                  <li><a href="/rewriter" className="text-gray-600 hover:text-gray-900">Content Rewriter</a></li>
                  <li><a href="/faq" className="text-gray-600 hover:text-gray-900">FAQ Generator</a></li>
                </ul>
              </div>
              
              {/* About */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-4">About</h4>
                <p className="text-sm text-gray-600">
                  A dual-engine strategy that captures organic traffic wherever your customers are searching.
                </p>
              </div>
            </div>
            
            <div className="border-t border-gray-200 mt-8 pt-8 text-center text-sm text-gray-500">
              © 2025 GEO Tool. Optimize for Google + AI Search.
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
