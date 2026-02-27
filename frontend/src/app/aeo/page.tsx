'use client';

import { useState } from 'react';
import { Loader2, MessageCircleQuestion, Check, X, Lightbulb, Target } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface AEOResult {
  url: string;
  score: number;
  grade: string;
  word_count: number;
  breakdown: {
    question_answer_patterns: { score: number; max: number; label: string };
    snippet_readiness: { score: number; max: number; label: string };
    first_sentence_clarity: { score: number; max: number; label: string };
    quotability: { score: number; max: number; label: string };
    paa_coverage: { score: number; max: number; label: string };
  };
  issues: {
    category: string;
    issue: string;
    impact: string;
    fix: string;
    predicted_impact?: string;
    example?: string;
    bad_example?: string;
    good_example?: string;
  }[];
  quick_wins: string[];
  details: {
    questions_detected: number;
    questions_with_answers: number;
    snippet_ready_blocks: number;
    quotable_statements: number;
    paa_questions_covered: number;
  };
  metadata?: {
    title?: string;
    description?: string;
  };
}

export default function AEOPage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AEOResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
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
      const response = await fetch(`${API_URL}/api/analyze/aeo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: urlToCheck }),
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to analyze AEO');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to analyze');
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

  const getCategoryColor = (score: number, max: number) => {
    const ratio = score / max;
    if (ratio >= 0.7) return 'bg-green-500';
    if (ratio >= 0.4) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getLabelColor = (label: string) => {
    if (label === 'Excellent') return 'text-green-600 bg-green-50';
    if (label === 'Good') return 'text-blue-600 bg-blue-50';
    if (label === 'Needs Work') return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🎯 Answer Engine Optimization
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Analyze how well your content is structured for AI extraction. 
          Optimize for ChatGPT, Perplexity, and Google AI Overviews.
        </p>
      </div>

      {/* URL Input */}
      <form onSubmit={handleAnalyze} className="max-w-3xl mx-auto">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <MessageCircleQuestion className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter URL to analyze (e.g., example.com)"
              className="w-full pl-12 pr-4 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-4 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
          >
            {loading && <Loader2 className="w-5 h-5 animate-spin" />}
            {loading ? 'Analyzing...' : 'Analyze AEO'}
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
          <p className="mt-4 text-gray-600">Analyzing answer extractability...</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto">
          {/* Page Info */}
          {result.metadata?.title && (
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold">{result.metadata.title}</h3>
              <p className="text-sm text-gray-500">{result.url}</p>
            </div>
          )}

          {/* Score Card & Key Metrics */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* Main Score */}
            <div className={`bg-gradient-to-br ${getScoreBg(result.score)} rounded-2xl p-6 text-white text-center shadow-xl`}>
              <div className="text-sm font-medium opacity-90 mb-2">AEO SCORE</div>
              <div className="text-6xl font-bold">{result.score}</div>
              <div className="text-lg mt-2">Grade: {result.grade}</div>
            </div>

            {/* Key Metrics */}
            <div className="bg-white rounded-2xl p-6 shadow-lg col-span-2">
              <h3 className="font-semibold text-lg mb-4">📊 Key Metrics</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-2xl font-bold text-indigo-600">
                    {result.details.questions_detected}
                  </div>
                  <div className="text-xs text-gray-600">Questions Found</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-2xl font-bold text-green-600">
                    {result.details.questions_with_answers}
                  </div>
                  <div className="text-xs text-gray-600">With Direct Answers</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-2xl font-bold text-blue-600">
                    {result.details.snippet_ready_blocks}
                  </div>
                  <div className="text-xs text-gray-600">Snippet-Ready Blocks</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-2xl font-bold text-purple-600">
                    {result.details.quotable_statements}
                  </div>
                  <div className="text-xs text-gray-600">Quotable Statements</div>
                </div>
              </div>
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="font-semibold text-lg mb-4">📈 Score Breakdown</h3>
            <div className="space-y-4">
              {Object.entries(result.breakdown).map(([key, data]) => (
                <div key={key} className="flex items-center gap-4">
                  <div className="w-48 text-sm text-gray-700 capitalize">
                    {key.replace(/_/g, ' ')}
                  </div>
                  <div className="flex-1">
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${getCategoryColor(data.score, data.max)}`}
                        style={{ width: `${(data.score / data.max) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="w-16 text-sm font-medium text-right">
                    {data.score}/{data.max}
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getLabelColor(data.label)}`}>
                    {data.label}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Wins */}
          {result.quick_wins && result.quick_wins.length > 0 && (
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-yellow-500" />
                Quick Wins
              </h3>
              <div className="grid md:grid-cols-2 gap-3">
                {result.quick_wins.map((win, index) => (
                  <div key={index} className="bg-white p-3 rounded-lg text-sm flex items-start gap-2">
                    <Target className="w-4 h-4 text-indigo-500 mt-0.5 flex-shrink-0" />
                    {win}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Issues */}
          {result.issues && result.issues.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold text-lg mb-4">⚠️ Issues to Fix</h3>
              <div className="space-y-4">
                {result.issues.map((issue, index) => {
                  const impactColors: Record<string, string> = {
                    critical: 'border-red-500 bg-red-50',
                    high: 'border-orange-500 bg-orange-50',
                    medium: 'border-yellow-500 bg-yellow-50',
                    low: 'border-blue-500 bg-blue-50',
                  };
                  return (
                    <div key={index} className={`border-l-4 p-4 rounded-r-lg ${impactColors[issue.impact] || impactColors.medium}`}>
                      <div className="flex items-start justify-between">
                        <div className="font-medium">{issue.issue}</div>
                        <span className="text-xs px-2 py-1 bg-white rounded capitalize">
                          {issue.impact}
                        </span>
                      </div>
                      {issue.fix && (
                        <div className="text-sm mt-2">
                          <strong>Fix:</strong> {issue.fix}
                        </div>
                      )}
                      {issue.predicted_impact && (
                        <div className="text-sm text-indigo-600 mt-1">
                          Expected: {issue.predicted_impact}
                        </div>
                      )}
                      {(issue.bad_example || issue.good_example) && (
                        <div className="mt-3 grid md:grid-cols-2 gap-2 text-xs">
                          {issue.bad_example && (
                            <div className="bg-red-100 p-2 rounded">
                              <div className="font-semibold text-red-700">❌ Bad:</div>
                              <div className="text-red-800 italic">"{issue.bad_example}"</div>
                            </div>
                          )}
                          {issue.good_example && (
                            <div className="bg-green-100 p-2 rounded">
                              <div className="font-semibold text-green-700">✅ Good:</div>
                              <div className="text-green-800 italic">"{issue.good_example}"</div>
                            </div>
                          )}
                        </div>
                      )}
                      {issue.example && !issue.good_example && (
                        <div className="mt-2 text-xs bg-white p-2 rounded font-mono">
                          {issue.example}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Info Section */}
      {!result && !loading && (
        <div className="bg-white rounded-xl shadow-md p-6 max-w-4xl mx-auto">
          <h3 className="font-semibold text-lg mb-4">📖 What is Answer Engine Optimization (AEO)?</h3>
          
          <p className="text-gray-600 mb-6">
            AEO measures how well your content is structured for AI extraction. AI search engines like 
            ChatGPT, Perplexity, and Google AI Overviews don't just rank pages—they <strong>extract answers</strong>. 
            AEO ensures your content is easy for AI to quote, cite, and reference.
          </p>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div className="bg-indigo-50 p-4 rounded-lg">
              <h4 className="font-semibold text-indigo-800 mb-3">What AEO Analyzes</h4>
              <ul className="space-y-2 text-sm text-indigo-700">
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span><strong>Q&A Patterns:</strong> Questions in headers with direct answers</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span><strong>Snippet Readiness:</strong> Definitions, lists, tables</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span><strong>First-Sentence Clarity:</strong> Sections start with answers</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span><strong>Quotability:</strong> Standalone extractable statements</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span><strong>PAA Coverage:</strong> What, How, Why question types</span>
                </li>
              </ul>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold text-green-800 mb-3">AEO Best Practices</h4>
              <ul className="space-y-2 text-sm text-green-700">
                <li className="flex items-start gap-2">
                  <Target className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>Use questions as H2/H3 headers</span>
                </li>
                <li className="flex items-start gap-2">
                  <Target className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>Answer questions in the first sentence</span>
                </li>
                <li className="flex items-start gap-2">
                  <Target className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>Add clear definitions ("X is...")</span>
                </li>
                <li className="flex items-start gap-2">
                  <Target className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>Use specific subjects, not "this" or "it"</span>
                </li>
                <li className="flex items-start gap-2">
                  <Target className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>Keep paragraphs 40-60 words for extraction</span>
                </li>
              </ul>
            </div>
          </div>

          <div className="bg-gray-100 p-4 rounded-lg">
            <h4 className="font-semibold mb-3">Example: Good vs Bad for AI Extraction</h4>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div className="bg-red-50 p-3 rounded border border-red-200">
                <div className="font-semibold text-red-700 mb-1">❌ Hard to Extract</div>
                <p className="text-red-800 italic">
                  "In this section, we'll discuss SEO. It's something you should know about. 
                  This helps with rankings..."
                </p>
              </div>
              <div className="bg-green-50 p-3 rounded border border-green-200">
                <div className="font-semibold text-green-700 mb-1">✅ Easy to Extract</div>
                <p className="text-green-800 italic">
                  "SEO (Search Engine Optimization) is the practice of optimizing websites 
                  to rank higher in search results and drive organic traffic."
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
