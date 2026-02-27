'use client';

import { useState } from 'react';
import { Loader2, FileText, Copy, Check, Download } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ArticleResult {
  title: string;
  meta_description: string;
  article: string;
  faq: { question: string; answer: string }[];
  schema: string;
  faq_schema: string;
  keywords_used: string[];
  word_count: number;
  geo_optimizations: string[];
  error?: string;
}

export default function ArticleGeneratorPage() {
  const [keywords, setKeywords] = useState('');
  const [instructions, setInstructions] = useState('');
  const [wordCount, setWordCount] = useState(1500);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ArticleResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const keywordList = keywords.split('\n').map(k => k.trim()).filter(k => k);
    
    if (keywordList.length === 0) {
      setError('Please enter at least one keyword');
      return;
    }
    
    if (keywordList.length > 5) {
      setError('Maximum 5 keywords allowed');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/generate/article`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keywords: keywordList,
          instructions: instructions || null,
          word_count: wordCount
        }),
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to generate article');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to generate article');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text: string, type: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
  };

  const handleDownload = () => {
    if (!result) return;
    
    const content = `# ${result.title}\n\n${result.meta_description}\n\n---\n\n${result.article}`;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${result.title.slice(0, 50).replace(/[^a-z0-9]/gi, '-')}.md`;
    a.click();
  };

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          ✍️ AI Article Generator
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Generate SEO + GEO optimized articles in seconds. 
          AI creates content optimized for both Google AND AI search engines.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleGenerate} className="max-w-3xl mx-auto space-y-6">
        {/* Keywords */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Keywords (1-5, one per line)
          </label>
          <textarea
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            placeholder="content marketing strategy&#10;SEO best practices&#10;digital content creation"
          />
        </div>

        {/* Instructions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom Instructions (optional)
          </label>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            className="w-full h-24 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            placeholder="- Write in a professional but conversational tone&#10;- Target audience: marketing professionals&#10;- Include actionable tips"
          />
        </div>

        {/* Word Count */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Word Count: {wordCount}
          </label>
          <input
            type="range"
            min="800"
            max="3000"
            step="100"
            value={wordCount}
            onChange={(e) => setWordCount(parseInt(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>800</span>
            <span>1500</span>
            <span>2000</span>
            <span>3000</span>
          </div>
        </div>

        {/* Generate Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-4 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium text-lg"
        >
          {loading && <Loader2 className="w-5 h-5 animate-spin" />}
          {loading ? 'Generating Article... (30-60 seconds)' : 'Generate Article'}
        </button>
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
          <Loader2 className="w-16 h-16 animate-spin mx-auto text-indigo-600" />
          <p className="mt-4 text-gray-600">AI is writing your article...</p>
          <p className="text-sm text-gray-400 mt-2">This may take 30-60 seconds</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">{result.word_count}</div>
              <div className="text-sm text-green-800">Words</div>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">{result.faq?.length || 0}</div>
              <div className="text-sm text-blue-800">FAQs</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-600">{result.geo_optimizations?.length || 0}</div>
              <div className="text-sm text-purple-800">GEO Optimizations</div>
            </div>
          </div>

          {/* GEO Optimizations */}
          {result.geo_optimizations && result.geo_optimizations.length > 0 && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h3 className="font-semibold text-purple-800 mb-2">🎯 GEO Optimizations Applied</h3>
              <ul className="space-y-1">
                {result.geo_optimizations.map((opt, i) => (
                  <li key={i} className="text-sm text-purple-700 flex items-center gap-2">
                    <Check className="w-4 h-4" /> {opt}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Title & Meta */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">Title & Meta Description</h3>
              <button
                onClick={() => handleCopy(`${result.title}\n\n${result.meta_description}`, 'meta')}
                className="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800"
              >
                {copied === 'meta' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                Copy
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <div className="text-xs text-gray-500 mb-1">Title ({result.title.length} chars)</div>
                <div className="text-blue-600 font-medium">{result.title}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Meta Description ({result.meta_description.length} chars)</div>
                <div className="text-gray-600">{result.meta_description}</div>
              </div>
            </div>
          </div>

          {/* Article */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">Article Content</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => handleCopy(result.article, 'article')}
                  className="flex items-center gap-1 px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
                >
                  {copied === 'article' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  Copy
                </button>
                <button
                  onClick={handleDownload}
                  className="flex items-center gap-1 px-3 py-1 text-sm bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200"
                >
                  <Download className="w-4 h-4" />
                  Download
                </button>
              </div>
            </div>
            <div className="prose prose-sm max-w-none max-h-96 overflow-y-auto p-4 bg-gray-50 rounded-lg">
              <pre className="whitespace-pre-wrap text-sm">{result.article}</pre>
            </div>
          </div>

          {/* FAQ */}
          {result.faq && result.faq.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-lg">FAQ Section</h3>
                <button
                  onClick={() => handleCopy(result.faq_schema, 'faq')}
                  className="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800"
                >
                  {copied === 'faq' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  Copy Schema
                </button>
              </div>
              <div className="space-y-3">
                {result.faq.map((item, i) => (
                  <details key={i} className="bg-gray-50 rounded-lg">
                    <summary className="p-3 cursor-pointer font-medium">{item.question}</summary>
                    <p className="px-3 pb-3 text-gray-600">{item.answer}</p>
                  </details>
                ))}
              </div>
            </div>
          )}

          {/* Schema */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">Schema Markup (JSON-LD)</h3>
              <button
                onClick={() => handleCopy(result.schema + '\n\n' + result.faq_schema, 'schema')}
                className="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800"
              >
                {copied === 'schema' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                Copy All
              </button>
            </div>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-xs max-h-48">
              {result.schema}
            </pre>
          </div>
        </div>
      )}

      {/* Info */}
      {!result && !loading && (
        <div className="bg-white rounded-xl shadow-md p-6 max-w-3xl mx-auto">
          <h3 className="font-semibold text-lg mb-4">✨ What Makes Our Articles Special</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl">📊</span>
              <div>
                <div className="font-medium">Statistics Included</div>
                <div className="text-sm text-gray-600">Real data points that AI loves to cite</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-2xl">💬</span>
              <div>
                <div className="font-medium">Expert Quotes</div>
                <div className="text-sm text-gray-600">Quotable content for AI extraction</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-2xl">❓</span>
              <div>
                <div className="font-medium">FAQ Section</div>
                <div className="text-sm text-gray-600">With schema markup for rich results</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-2xl">🎯</span>
              <div>
                <div className="font-medium">Answer Blocks</div>
                <div className="text-sm text-gray-600">40-60 word sections AI can directly quote</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
