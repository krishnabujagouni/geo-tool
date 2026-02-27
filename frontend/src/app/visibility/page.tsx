'use client';

import { useState } from 'react';
import { Loader2, Search, Check, X, AlertTriangle, Copy, Eye } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CrawlerStatus {
  name: string;
  owner: string;
  status: 'allowed' | 'blocked';
}

interface VisibilityResult {
  url: string;
  overall_score: number;
  overall_status: 'visible' | 'partial' | 'blocked';
  robots_txt: {
    status: string;
    url: string;
    ai_allowed: boolean;
    crawlers: CrawlerStatus[];
    details: string;
  };
  sitemap_xml: {
    status: string;
    url: string;
    urls_count: number;
    details: string;
  };
  llms_txt: {
    status: string;
    url: string;
    details: string;
  };
  recommendations: {
    priority: number;
    file: string;
    issue: string;
    action: string;
    impact: string;
  }[];
  templates: {
    robots_txt: string;
    sitemap_xml: string;
    llms_txt: string;
  };
}

export default function VisibilityPage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VisibilityResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTemplate, setActiveTemplate] = useState<'robots' | 'sitemap' | 'llms' | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

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
      const response = await fetch(`${API_URL}/api/visibility`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: urlToCheck }),
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to check visibility');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to check visibility');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text: string, type: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
  };

  const getStatusIcon = (status: string) => {
    if (status === 'found') return <Check className="w-5 h-5 text-green-500" />;
    if (status === 'not_found') return <X className="w-5 h-5 text-red-500" />;
    return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
  };

  const getStatusBg = (status: string) => {
    if (status === 'visible') return 'from-green-500 to-emerald-600';
    if (status === 'partial') return 'from-yellow-500 to-orange-500';
    return 'from-red-500 to-rose-600';
  };

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🔍 AI Visibility Checker
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Check if your website is allowing AI search crawlers to access your content.
          Get templates for robots.txt, sitemap.xml, and llms.txt.
        </p>
      </div>

      {/* URL Input */}
      <form onSubmit={handleCheck} className="max-w-3xl mx-auto">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Eye className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter your domain (e.g., example.com)"
              className="w-full pl-12 pr-4 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-lg"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-4 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
          >
            {loading && <Loader2 className="w-5 h-5 animate-spin" />}
            {loading ? 'Checking...' : 'Check Visibility'}
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
          <p className="mt-4 text-gray-600">Checking AI visibility...</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-8 animate-fadeIn">
          {/* Overall Score */}
          <div className={`bg-gradient-to-br ${getStatusBg(result.overall_status)} rounded-2xl p-8 text-white text-center shadow-xl max-w-md mx-auto`}>
            <div className="text-sm font-medium opacity-90 mb-2">AI VISIBILITY SCORE</div>
            <div className="text-7xl font-bold">{result.overall_score}</div>
            <div className="text-xl mt-2 capitalize">{result.overall_status}</div>
          </div>

          {/* Three Files Status */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* robots.txt */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-lg">robots.txt</h3>
                {getStatusIcon(result.robots_txt.status)}
              </div>
              <p className="text-gray-600 text-sm mb-2">{result.robots_txt.details}</p>
              <div className="text-xs text-gray-400">
                {result.robots_txt.status === 'found' ? '✅ Found' : '❌ Missing'}
              </div>
              
              {result.robots_txt.crawlers && result.robots_txt.crawlers.length > 0 && (
                <div className="mt-4 space-y-1">
                  <div className="text-xs font-medium text-gray-500">AI Crawlers:</div>
                  {result.robots_txt.crawlers.slice(0, 4).map((crawler, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <span>{crawler.name}</span>
                      <span className={crawler.status === 'allowed' ? 'text-green-500' : 'text-red-500'}>
                        {crawler.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* sitemap.xml */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-lg">sitemap.xml</h3>
                {getStatusIcon(result.sitemap_xml.status)}
              </div>
              <p className="text-gray-600 text-sm mb-2">{result.sitemap_xml.details}</p>
              <div className="text-xs text-gray-400">
                {result.sitemap_xml.status === 'found' 
                  ? `✅ ${result.sitemap_xml.urls_count} URLs found` 
                  : '❌ Missing'}
              </div>
            </div>

            {/* llms.txt */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-lg">llms.txt</h3>
                {getStatusIcon(result.llms_txt.status)}
              </div>
              <p className="text-gray-600 text-sm mb-2">{result.llms_txt.details}</p>
              <div className="text-xs text-gray-400">
                {result.llms_txt.status === 'found' ? '✅ Found' : '⚠️ Recommended'}
              </div>
            </div>
          </div>

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold text-lg mb-4">📋 Recommendations</h3>
              <div className="space-y-3">
                {result.recommendations.map((rec, index) => (
                  <div key={index} className="border-l-4 border-indigo-500 pl-4 py-2">
                    <div className="flex items-center gap-2">
                      <span className="bg-indigo-100 text-indigo-700 text-xs font-bold px-2 py-1 rounded">
                        {rec.file}
                      </span>
                      <span className="font-medium">{rec.issue}</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">👉 {rec.action}</p>
                    <p className="text-xs text-indigo-600 mt-1">Impact: {rec.impact}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* File Templates */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="font-semibold text-lg mb-4">📄 Ready-to-Use Templates</h3>
            <p className="text-gray-600 text-sm mb-4">
              Click on a file to see the template. Copy and upload to your website root.
            </p>
            
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setActiveTemplate(activeTemplate === 'robots' ? null : 'robots')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  activeTemplate === 'robots' 
                    ? 'bg-indigo-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                robots.txt
              </button>
              <button
                onClick={() => setActiveTemplate(activeTemplate === 'sitemap' ? null : 'sitemap')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  activeTemplate === 'sitemap' 
                    ? 'bg-indigo-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                sitemap.xml
              </button>
              <button
                onClick={() => setActiveTemplate(activeTemplate === 'llms' ? null : 'llms')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  activeTemplate === 'llms' 
                    ? 'bg-indigo-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                llms.txt
              </button>
            </div>

            {activeTemplate && (
              <div className="relative">
                <button
                  onClick={() => handleCopy(
                    activeTemplate === 'robots' ? result.templates.robots_txt :
                    activeTemplate === 'sitemap' ? result.templates.sitemap_xml :
                    result.templates.llms_txt,
                    activeTemplate
                  )}
                  className="absolute top-2 right-2 flex items-center gap-1 px-3 py-1 bg-white rounded-lg shadow text-sm hover:bg-gray-50"
                >
                  {copied === activeTemplate ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied === activeTemplate ? 'Copied!' : 'Copy'}
                </button>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm max-h-96">
                  {activeTemplate === 'robots' && result.templates.robots_txt}
                  {activeTemplate === 'sitemap' && result.templates.sitemap_xml}
                  {activeTemplate === 'llms' && result.templates.llms_txt}
                </pre>
              </div>
            )}
          </div>

          {/* Next Steps */}
          <div className="bg-indigo-50 rounded-xl p-6">
            <h3 className="font-semibold text-lg mb-4">✅ Next Steps</h3>
            <ol className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="bg-indigo-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm flex-shrink-0">1</span>
                <span>Download/copy the templates above</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="bg-indigo-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm flex-shrink-0">2</span>
                <span>Upload to your website root directory (yoursite.com/robots.txt, etc.)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="bg-indigo-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm flex-shrink-0">3</span>
                <span>Submit sitemap to Google Search Console</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="bg-indigo-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm flex-shrink-0">4</span>
                <span>Check back in 48-72 hours to verify AI crawlers have indexed your site</span>
              </li>
            </ol>
          </div>
        </div>
      )}

      {/* Info Section (shown when no result) */}
      {!result && !loading && (
        <div className="bg-white rounded-xl shadow-md p-6 max-w-4xl mx-auto">
          <h3 className="font-semibold text-lg mb-4">📚 Essential Files for AI Visibility</h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-3">File</th>
                  <th className="text-left py-2 px-3">Purpose</th>
                  <th className="text-left py-2 px-3">Target</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-3 px-3 font-medium">robots.txt</td>
                  <td className="py-3 px-3">🛑 Permission - Allow/Block crawlers</td>
                  <td className="py-3 px-3">All web crawlers</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-3 font-medium">sitemap.xml</td>
                  <td className="py-3 px-3">📍 Discovery - List all your pages</td>
                  <td className="py-3 px-3">Google, Bing, AI</td>
                </tr>
                <tr>
                  <td className="py-3 px-3 font-medium">llms.txt</td>
                  <td className="py-3 px-3">🧠 Understanding - Explain your site</td>
                  <td className="py-3 px-3">ChatGPT, Claude, Perplexity</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
