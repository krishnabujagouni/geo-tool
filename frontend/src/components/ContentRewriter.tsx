'use client';

import { useState } from 'react';
import { rewriteContent, RewriteResult } from '@/lib/api';
import { Loader2, ArrowRight } from 'lucide-react';

const IMPROVEMENTS = [
  { id: 'add_statistics', label: 'Add Statistics', description: 'Add data and percentages' },
  { id: 'add_citations', label: 'Add Citations', description: 'Reference credible sources' },
  { id: 'add_quotes', label: 'Add Expert Quotes', description: 'Include expert opinions' },
  { id: 'simplify_language', label: 'Simplify Language', description: 'Improve readability' },
  { id: 'create_answer_blocks', label: 'Create Answer Blocks', description: '40-60 word chunks' },
  { id: 'add_definitions', label: 'Add Definitions', description: 'Define key terms' },
];

export function ContentRewriter() {
  const [content, setContent] = useState('');
  const [selectedImprovements, setSelectedImprovements] = useState<string[]>(['add_statistics', 'simplify_language']);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RewriteResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const toggleImprovement = (id: string) => {
    setSelectedImprovements(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id)
        : [...prev, id]
    );
  };

  const handleRewrite = async () => {
    if (!content.trim()) {
      setError('Please enter some content');
      return;
    }
    if (selectedImprovements.length === 0) {
      setError('Please select at least one improvement');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await rewriteContent(content, selectedImprovements);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to rewrite content');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Content Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Paste content to improve
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Paste your content here..."
        />
      </div>

      {/* Improvement Options */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select improvements
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {IMPROVEMENTS.map(imp => (
            <button
              key={imp.id}
              onClick={() => toggleImprovement(imp.id)}
              className={`p-3 rounded-lg border text-left transition-all ${
                selectedImprovements.includes(imp.id)
                  ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="font-medium text-sm">{imp.label}</div>
              <div className="text-xs text-gray-500">{imp.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Rewrite Button */}
      <button
        onClick={handleRewrite}
        disabled={loading}
        className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
      >
        {loading && <Loader2 className="w-4 h-4 animate-spin" />}
        {loading ? 'Rewriting with AI...' : 'Rewrite Content'}
        {!loading && <ArrowRight className="w-4 h-4" />}
      </button>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Results */}
      {result && result.rewritten && (
        <div className="space-y-6 animate-fadeIn">
          {/* Score Increase */}
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 text-green-700">
              <span className="text-2xl">📈</span>
              <span className="font-semibold">
                Predicted score increase: +{result.predicted_score_increase} points
              </span>
            </div>
          </div>

          {/* Changes Made */}
          <div>
            <h3 className="font-semibold mb-3">Changes Made ({result.changes.length})</h3>
            <div className="space-y-2">
              {result.changes.map((change, index) => (
                <div key={index} className="flex items-start gap-2 text-sm">
                  <span className="text-green-500">✓</span>
                  <span>
                    <span className="font-medium">{change.type}:</span> {change.description}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Comparison */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold mb-2 text-gray-500">Original</h3>
              <div className="p-4 bg-gray-50 rounded-lg text-sm max-h-96 overflow-y-auto whitespace-pre-wrap">
                {result.original}
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-2 text-indigo-600">Rewritten</h3>
              <div className="p-4 bg-indigo-50 rounded-lg text-sm max-h-96 overflow-y-auto whitespace-pre-wrap border-2 border-indigo-200">
                {result.rewritten}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
