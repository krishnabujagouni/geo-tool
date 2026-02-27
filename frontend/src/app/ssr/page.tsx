'use client';

import { useState } from 'react';
import { Loader2, Server, Check, X, AlertTriangle } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SSRResult {
  url: string;
  is_ssr: boolean;
  render_type: string;
  score: number;
  grade: string;
  checks: {
    content_in_html: {
      content_length: number;
      word_count: number;
      paragraph_count: number;
      has_substantial_content: boolean;
    };
    meta_tags: {
      has_title: boolean;
      title_text: string | null;
      has_description: boolean;
      description_text: string | null;
      has_og_tags: boolean;
      has_canonical: boolean;
    };
    headings: {
      has_h1: boolean;
      h1_text: string | null;
      h2_count: number;
      proper_hierarchy: boolean;
    };
    framework: {
      framework: string | null;
      is_ssr_framework: boolean;
      indicators: string[];
    };
    js_indicators: {
      has_empty_root: boolean;
      has_loading_indicator: boolean;
      has_noscript_fallback: boolean;
    };
  };
  issues: {
    severity: string;
    issue: string;
    detail: string;
  }[];
  recommendations: {
    priority: number;
    title: string;
    description: string;
    action: string;
    impact: string;
  }[];
  error?: string;
}

export default function SSRCheckerPage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SSRResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    let urlToCheck = url.trim();
    if (!urlToCheck.startsWith('http')) {
      urlToCheck = 'https://' + urlToCheck;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/ssr-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: urlToCheck }),
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to check SSR');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to check SSR');
    } finally {
      setLoading(false);
    }
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'from-green-500 to-emerald-600';
    if (score >= 60) return 'from-blue-500 to-indigo-600';
    if (score >= 40) return 'from-yellow-500 to-orange-500';
    return 'from-red-500 to-rose-600';
  };

  const getRenderTypeBadge = (type: string) => {
    const styles: Record<string, string> = {
      'SSR': 'bg-green-100 text-green-800',
      'Static': 'bg-green-100 text-green-800',
      'Hybrid': 'bg-blue-100 text-blue-800',
      'Partial CSR': 'bg-yellow-100 text-yellow-800',
      'CSR': 'bg-red-100 text-red-800',
    };
    return styles[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          ⚙️ SSR Checker
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Check if your website is server-side rendered. 
          CSR sites may be invisible to AI crawlers and search engines.
        </p>
      </div>

      {/* URL Input */}
      <form onSubmit={handleCheck} className="max-w-3xl mx-auto">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Server className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter URL to check (e.g., example.com)"
              className="w-full pl-12 pr-4 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-4 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
          >
            {loading && <Loader2 className="w-5 h-5 animate-spin" />}
            {loading ? 'Checking...' : 'Check SSR'}
          </button>
        </div>
      </form>

      {/* Error */}
      {error && (
        <div className="max-w-3xl mx-auto p-4 bg-red-50 text-red-700 rounded-lg text-center">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-12">
          <Loader2 className="w-12 h-12 animate-spin mx-auto text-indigo-600" />
          <p className="mt-4 text-gray-600">Analyzing page rendering...</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
          {/* Score Card */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className={`bg-gradient-to-br ${getScoreBg(result.score)} rounded-2xl p-6 text-white text-center shadow-xl`}>
              <div className="text-sm font-medium opacity-90 mb-2">SSR SCORE</div>
              <div className="text-6xl font-bold">{result.score}</div>
              <div className="text-lg mt-2">Grade: {result.grade}</div>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg flex flex-col justify-center items-center">
              <div className="text-sm text-gray-500 mb-2">RENDER TYPE</div>
              <span className={`px-4 py-2 rounded-full text-lg font-semibold ${getRenderTypeBadge(result.render_type)}`}>
                {result.render_type}
              </span>
              <div className="mt-4 text-center">
                {result.is_ssr ? (
                  <div className="text-green-600 flex items-center gap-2 justify-center">
                    <Check className="w-5 h-5" />
                    SEO & AI Ready
                  </div>
                ) : (
                  <div className="text-red-600 flex items-center gap-2 justify-center">
                    <X className="w-5 h-5" />
                    Needs Improvement
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Framework Detection */}
          {result.checks.framework.framework && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold text-lg mb-3">🔧 Framework Detected</h3>
              <div className="flex items-center gap-3">
                <span className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full font-medium">
                  {result.checks.framework.framework}
                </span>
                {result.checks.framework.is_ssr_framework ? (
                  <span className="text-green-600 text-sm">✓ SSR Capable</span>
                ) : (
                  <span className="text-yellow-600 text-sm">⚠ Typically CSR</span>
                )}
              </div>
              {result.checks.framework.indicators.length > 0 && (
                <div className="mt-2 text-sm text-gray-600">
                  {result.checks.framework.indicators.join(', ')}
                </div>
              )}
            </div>
          )}

          {/* Detailed Checks */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Content Check */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold text-lg mb-4">📄 Content in HTML</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Content Length</span>
                  <span className="font-medium">{result.checks.content_in_html.content_length.toLocaleString()} chars</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Word Count</span>
                  <span className="font-medium">{result.checks.content_in_html.word_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Paragraphs</span>
                  <span className="font-medium">{result.checks.content_in_html.paragraph_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Substantial Content</span>
                  {result.checks.content_in_html.has_substantial_content ? (
                    <Check className="w-5 h-5 text-green-500" />
                  ) : (
                    <X className="w-5 h-5 text-red-500" />
                  )}
                </div>
              </div>
            </div>

            {/* Meta Tags */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold text-lg mb-4">🏷️ Meta Tags</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Title Tag</span>
                  {result.checks.meta_tags.has_title ? (
                    <Check className="w-5 h-5 text-green-500" />
                  ) : (
                    <X className="w-5 h-5 text-red-500" />
                  )}
                </div>
                {result.checks.meta_tags.title_text && (
                  <div className="text-sm text-gray-500 truncate">
                    "{result.checks.meta_tags.title_text}"
                  </div>
                )}
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Meta Description</span>
                  {result.checks.meta_tags.has_description ? (
                    <Check className="w-5 h-5 text-green-500" />
                  ) : (
                    <X className="w-5 h-5 text-red-500" />
                  )}
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Open Graph Tags</span>
                  {result.checks.meta_tags.has_og_tags ? (
                    <Check className="w-5 h-5 text-green-500" />
                  ) : (
                    <X className="w-5 h-5 text-red-500" />
                  )}
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Canonical Tag</span>
                  {result.checks.meta_tags.has_canonical ? (
                    <Check className="w-5 h-5 text-green-500" />
                  ) : (
                    <X className="w-5 h-5 text-red-500" />
                  )}
                </div>
              </div>
            </div>

            {/* Headings */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold text-lg mb-4">📑 Heading Structure</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">H1 Tag</span>
                  {result.checks.headings.has_h1 ? (
                    <Check className="w-5 h-5 text-green-500" />
                  ) : (
                    <X className="w-5 h-5 text-red-500" />
                  )}
                </div>
                {result.checks.headings.h1_text && (
                  <div className="text-sm text-gray-500 truncate">
                    "{result.checks.headings.h1_text}"
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">H2 Count</span>
                  <span className="font-medium">{result.checks.headings.h2_count}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Proper Hierarchy</span>
                  {result.checks.headings.proper_hierarchy ? (
                    <Check className="w-5 h-5 text-green-500" />
                  ) : (
                    <X className="w-5 h-5 text-red-500" />
                  )}
                </div>
              </div>
            </div>

            {/* JS Indicators */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold text-lg mb-4">⚡ JS Rendering Indicators</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Empty Root Div</span>
                  {result.checks.js_indicators.has_empty_root ? (
                    <span className="text-red-500 text-sm">⚠ Detected (CSR)</span>
                  ) : (
                    <Check className="w-5 h-5 text-green-500" />
                  )}
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Loading Indicator</span>
                  {result.checks.js_indicators.has_loading_indicator ? (
                    <span className="text-yellow-500 text-sm">⚠ Found</span>
                  ) : (
                    <Check className="w-5 h-5 text-green-500" />
                  )}
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Noscript Fallback</span>
                  {result.checks.js_indicators.has_noscript_fallback ? (
                    <Check className="w-5 h-5 text-green-500" />
                  ) : (
                    <span className="text-yellow-500 text-sm">⚠ Missing</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Issues */}
          {result.issues && result.issues.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold text-lg mb-4">⚠️ Issues Found</h3>
              <div className="space-y-3">
                {result.issues.map((issue, index) => {
                  const severityStyles: Record<string, string> = {
                    critical: 'bg-red-100 border-red-500 text-red-800',
                    high: 'bg-orange-100 border-orange-500 text-orange-800',
                    medium: 'bg-yellow-100 border-yellow-500 text-yellow-800',
                  };
                  return (
                    <div key={index} className={`border-l-4 p-3 rounded-r-lg ${severityStyles[issue.severity] || severityStyles.medium}`}>
                      <div className="font-medium">{issue.issue}</div>
                      <div className="text-sm opacity-80">{issue.detail}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold text-lg mb-4">💡 Recommendations</h3>
              <div className="space-y-4">
                {result.recommendations.map((rec, index) => (
                  <div key={index} className="border-l-4 border-indigo-500 pl-4 py-2">
                    <div className="flex items-center gap-2">
                      <span className="bg-indigo-100 text-indigo-700 text-xs font-bold px-2 py-1 rounded">
                        #{rec.priority}
                      </span>
                      <h4 className="font-semibold">{rec.title}</h4>
                    </div>
                    <p className="text-gray-600 text-sm mt-1">{rec.description}</p>
                    <p className="text-sm mt-1"><strong>Action:</strong> {rec.action}</p>
                    <p className="text-sm text-indigo-600 mt-1">Impact: {rec.impact}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Info Section */}
      {!result && !loading && (
        <div className="bg-white rounded-xl shadow-md p-6 max-w-4xl mx-auto">
          <h3 className="font-semibold text-lg mb-4">📖 What is SSR & Why It Matters</h3>
          
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold text-green-800 mb-2">✅ Server-Side Rendering (SSR)</h4>
              <p className="text-sm text-green-700">
                Content is generated on the server. Search engines and AI crawlers see your full content immediately.
              </p>
              <div className="mt-2 bg-white p-2 rounded text-xs font-mono">
                &lt;article&gt;Full content here...&lt;/article&gt;
              </div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <h4 className="font-semibold text-red-800 mb-2">❌ Client-Side Rendering (CSR)</h4>
              <p className="text-sm text-red-700">
                Content is loaded via JavaScript. Crawlers may see an empty page.
              </p>
              <div className="mt-2 bg-white p-2 rounded text-xs font-mono">
                &lt;div id="root"&gt;&lt;/div&gt; ← Empty!
              </div>
            </div>
          </div>

          <h4 className="font-semibold mb-3">SSR Frameworks</h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm">
            <div className="bg-gray-100 p-2 rounded text-center">Next.js ✓</div>
            <div className="bg-gray-100 p-2 rounded text-center">Nuxt.js ✓</div>
            <div className="bg-gray-100 p-2 rounded text-center">Astro ✓</div>
            <div className="bg-gray-100 p-2 rounded text-center">SvelteKit ✓</div>
            <div className="bg-gray-100 p-2 rounded text-center">Remix ✓</div>
          </div>
        </div>
      )}
    </div>
  );
}
