'use client';

import { useState } from 'react';
import { analyzeUrl, CombinedResult } from '@/lib/api';
import { Loader2, Search, TrendingUp, Globe, Bot, ChevronDown, ChevronUp } from 'lucide-react';

export default function AnalyzerPage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CombinedResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    let urlToAnalyze = url.trim();
    if (!urlToAnalyze.startsWith('http')) {
      urlToAnalyze = 'https://' + urlToAnalyze;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeUrl(urlToAnalyze);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to analyze URL');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-blue-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'from-green-500 to-emerald-600';
    if (score >= 60) return 'from-blue-500 to-indigo-600';
    if (score >= 40) return 'from-yellow-500 to-orange-500';
    return 'from-red-500 to-rose-600';
  };

  const getBarColor = (ratio: number) => {
    if (ratio >= 0.7) return 'bg-green-500';
    if (ratio >= 0.4) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
          SEO + GEO Analyzer
        </h1>
        <p className="text-lg text-gray-600">
          Analyze your content for both Google Search AND AI search engines. 
          Get a combined score with actionable recommendations.
        </p>
      </div>

      {/* URL Input */}
      <div className="bg-white rounded-2xl shadow-lg p-6 md:p-8 max-w-3xl mx-auto">
        <form onSubmit={handleAnalyze}>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Enter URL to analyze
          </label>
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="example.com/your-page"
                className="w-full pl-12 pr-4 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-lg"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-4 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
            >
              {loading && <Loader2 className="w-5 h-5 animate-spin" />}
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="max-w-3xl mx-auto p-4 bg-red-50 text-red-700 rounded-xl text-center">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-16">
          <Loader2 className="w-16 h-16 animate-spin mx-auto text-indigo-600" />
          <p className="mt-4 text-gray-600 text-lg">Analyzing SEO + GEO...</p>
          <p className="text-sm text-gray-400 mt-2">This may take 10-20 seconds</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-8 animate-fadeIn">
          {/* Page Info */}
          {result.metadata?.title && (
            <div className="bg-white rounded-xl shadow-md p-6 max-w-4xl mx-auto">
              <h2 className="font-semibold text-xl text-gray-900">{result.metadata.title}</h2>
              <p className="text-gray-500 text-sm mt-1">{result.url}</p>
              <p className="text-gray-400 text-sm">{result.word_count} words</p>
            </div>
          )}

          {/* Score Cards */}
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {/* Combined Score */}
            <div className={`bg-gradient-to-br ${getScoreBg(result.combined_score)} rounded-2xl p-8 text-white text-center shadow-xl`}>
              <div className="flex items-center justify-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5" />
                <span className="text-sm font-medium opacity-90">COMBINED SCORE</span>
              </div>
              <div className="text-7xl font-bold">{result.combined_score}</div>
              <div className="text-xl mt-2">Grade: {result.combined_grade}</div>
            </div>

            {/* SEO Score */}
            <div className="bg-white rounded-2xl p-8 text-center shadow-lg border-2 border-blue-100">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Globe className="w-5 h-5 text-blue-500" />
                <span className="text-sm font-medium text-gray-500">SEO (Google)</span>
              </div>
              <div className={`text-6xl font-bold ${getScoreColor(result.seo.score)}`}>
                {result.seo.score}
              </div>
              <div className="text-gray-500 mt-2">Grade: {result.seo.grade}</div>
            </div>

            {/* GEO Score */}
            <div className="bg-white rounded-2xl p-8 text-center shadow-lg border-2 border-purple-100">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Bot className="w-5 h-5 text-purple-500" />
                <span className="text-sm font-medium text-gray-500">GEO (AI Search)</span>
              </div>
              <div className={`text-6xl font-bold ${getScoreColor(result.geo.score)}`}>
                {result.geo.score}
              </div>
              <div className="text-gray-500 mt-2">Grade: {result.geo.grade}</div>
            </div>
          </div>

          {/* Breakdowns */}
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {/* SEO Breakdown */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <button
                onClick={() => setExpandedSection(expandedSection === 'seo' ? null : 'seo')}
                className="w-full p-6 flex items-center justify-between hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <Globe className="w-6 h-6 text-blue-500" />
                  <span className="font-semibold text-lg">SEO Breakdown</span>
                </div>
                {expandedSection === 'seo' ? <ChevronUp /> : <ChevronDown />}
              </button>
              
              {expandedSection === 'seo' && (
                <div className="px-6 pb-6 space-y-4">
                  {Object.entries(result.seo.breakdown).map(([key, data]) => (
                    <div key={key}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                        <span className="font-medium">{data.score}/{data.max}</span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${getBarColor(data.score / data.max)}`}
                          style={{ width: `${(data.score / data.max) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* GEO Breakdown */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <button
                onClick={() => setExpandedSection(expandedSection === 'geo' ? null : 'geo')}
                className="w-full p-6 flex items-center justify-between hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <Bot className="w-6 h-6 text-purple-500" />
                  <span className="font-semibold text-lg">GEO Breakdown</span>
                </div>
                {expandedSection === 'geo' ? <ChevronUp /> : <ChevronDown />}
              </button>
              
              {expandedSection === 'geo' && (
                <div className="px-6 pb-6 space-y-4">
                  {Object.entries(result.geo.breakdown).map(([key, data]) => (
                    <div key={key}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                        <span className="font-medium">{data.score}/{data.max}</span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${getBarColor(data.score / data.max)}`}
                          style={{ width: `${(data.score / data.max) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6 max-w-4xl mx-auto">
              <h3 className="font-semibold text-xl mb-6 flex items-center gap-2">
                🎯 Priority Recommendations
              </h3>
              <div className="space-y-6">
                {result.recommendations.map((rec, index) => (
                  <div key={index} className="border-l-4 border-indigo-500 pl-6 py-2">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="bg-indigo-600 text-white text-sm font-bold w-8 h-8 rounded-full flex items-center justify-center">
                        {rec.priority}
                      </span>
                      <h4 className="font-semibold text-lg">{rec.title}</h4>
                    </div>
                    <p className="text-gray-600 mb-3">{rec.description}</p>
                    <ul className="space-y-1 mb-3">
                      {rec.actions.map((action, i) => (
                        <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                          <span className="text-green-500 mt-0.5">✓</span>
                          {action}
                        </li>
                      ))}
                    </ul>
                    <p className="text-sm text-indigo-600 font-medium">
                      📈 {rec.impact}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Issues */}
          {result.unified_issues && result.unified_issues.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6 max-w-4xl mx-auto">
              <h3 className="font-semibold text-xl mb-6 flex items-center gap-2">
                ⚠️ Issues to Fix ({result.unified_issues.length})
              </h3>
              <div className="space-y-3">
                {result.unified_issues.map((issue, index) => {
                  const colors: Record<string, string> = {
                    critical: 'bg-red-50 border-red-400 text-red-800',
                    high: 'bg-orange-50 border-orange-400 text-orange-800',
                    medium: 'bg-yellow-50 border-yellow-400 text-yellow-800',
                    low: 'bg-blue-50 border-blue-400 text-blue-800',
                  };
                  const icons: Record<string, string> = {
                    critical: '🔴',
                    high: '🟠',
                    medium: '🟡',
                    low: '🟢',
                  };
                  
                  return (
                    <div key={index} className={`border-l-4 p-4 rounded-r-lg ${colors[issue.impact]}`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span>{icons[issue.impact]}</span>
                          <span className="font-medium">{issue.issue}</span>
                        </div>
                        <span className="text-xs uppercase opacity-70 bg-white/50 px-2 py-1 rounded">
                          {issue.source}
                        </span>
                      </div>
                      {issue.fix && (
                        <p className="text-sm mt-2 opacity-80">
                          <strong>Fix:</strong> {issue.fix}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="flex flex-wrap gap-4 justify-center max-w-4xl mx-auto">
            <a 
              href="/rewriter" 
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 font-medium flex items-center gap-2"
            >
              ✍️ Fix with AI Rewriter
            </a>
            <a 
              href="/faq" 
              className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 font-medium flex items-center gap-2"
            >
              ❓ Add FAQ Section
            </a>
            <a 
              href="/visibility" 
              className="px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 font-medium flex items-center gap-2"
            >
              👁️ Check AI Visibility
            </a>
          </div>
        </div>
      )}

      {/* Info Section */}
      {!result && !loading && (
        <div className="bg-white rounded-xl shadow-md p-8 max-w-4xl mx-auto">
          <h3 className="font-semibold text-xl mb-6 text-center">What We Analyze</h3>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <Globe className="w-8 h-8 text-blue-500" />
                <h4 className="font-semibold text-lg">SEO (Google)</h4>
              </div>
              <ul className="space-y-2 text-gray-600">
                <li>✓ Meta tags (title, description)</li>
                <li>✓ Content quality & length</li>
                <li>✓ Heading structure (H1, H2, H3)</li>
                <li>✓ Technical SEO (HTTPS, canonical)</li>
                <li>✓ Page performance</li>
              </ul>
            </div>
            
            <div>
              <div className="flex items-center gap-3 mb-4">
                <Bot className="w-8 h-8 text-purple-500" />
                <h4 className="font-semibold text-lg">GEO (AI Search)</h4>
              </div>
              <ul className="space-y-2 text-gray-600">
                <li>✓ Statistics & data points</li>
                <li>✓ Citations & sources</li>
                <li>✓ Expert quotes</li>
                <li>✓ Answer-ready blocks</li>
                <li>✓ AI crawler access</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
