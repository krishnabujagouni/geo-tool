'use client';

import { FAQGenerator } from '@/components/FAQGenerator';

export default function FAQPage() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI FAQ Generator
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Generate SEO-optimized FAQ sections with schema markup. AI creates questions real users would ask.
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-md p-6">
        <FAQGenerator />
      </div>
    </div>
  );
}
