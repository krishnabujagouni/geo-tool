'use client';

import { ContentRewriter } from '@/components/ContentRewriter';

export default function RewriterPage() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI Content Rewriter
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Use AI to improve your content for GEO. Add statistics, citations, expert quotes, and more with one click.
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-md p-6">
        <ContentRewriter />
      </div>
    </div>
  );
}
