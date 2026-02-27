'use client';

import { useState } from 'react';
import { generateFAQ, FAQResult } from '@/lib/api';
import { Loader2, Copy, Check } from 'lucide-react';

export function FAQGenerator() {
  const [content, setContent] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FAQResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<'schema' | 'html' | null>(null);

  const handleGenerate = async () => {
    if (!content.trim()) {
      setError('Please enter some content');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await generateFAQ(content, numQuestions);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to generate FAQ');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text: string, type: 'schema' | 'html') => {
    await navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Paste your content
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Paste your article content here..."
        />
      </div>

      <div className="flex items-center gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Number of FAQs
          </label>
          <input
            type="number"
            min={3}
            max={10}
            value={numQuestions}
            onChange={(e) => setNumQuestions(parseInt(e.target.value) || 5)}
            className="w-20 p-2 border border-gray-300 rounded-lg"
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="mt-6 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          {loading ? 'Generating...' : 'Generate FAQ'}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-6 animate-fadeIn">
          {/* Generated FAQs */}
          <div>
            <h3 className="font-semibold mb-3">Generated FAQs</h3>
            <div className="space-y-3">
              {result.faqs.map((faq, index) => (
                <details key={index} className="bg-gray-50 rounded-lg">
                  <summary className="p-4 cursor-pointer font-medium hover:bg-gray-100">
                    {faq.question}
                  </summary>
                  <p className="px-4 pb-4 text-gray-700">{faq.answer}</p>
                </details>
              ))}
            </div>
          </div>

          {/* Schema Markup */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold">JSON-LD Schema</h3>
              <button
                onClick={() => handleCopy(result.schema_markup, 'schema')}
                className="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800"
              >
                {copied === 'schema' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied === 'schema' ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
              {result.schema_markup}
            </pre>
          </div>

          {/* HTML */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold">HTML Code</h3>
              <button
                onClick={() => handleCopy(result.html, 'html')}
                className="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800"
              >
                {copied === 'html' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied === 'html' ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
              {result.html}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
