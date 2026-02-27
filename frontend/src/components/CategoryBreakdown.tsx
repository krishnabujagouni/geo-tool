'use client';

import { CategoryScore } from '@/lib/api';
import { getScoreColor } from '@/lib/utils';

interface CategoryBreakdownProps {
  breakdown: {
    citeability: CategoryScore;
    structure: CategoryScore;
    authority: CategoryScore;
    extractability: CategoryScore;
    technical: CategoryScore;
  };
}

const categories = [
  { key: 'citeability', name: 'Citeability', icon: '📝', description: 'Stats, citations, quotes' },
  { key: 'structure', name: 'Structure', icon: '🏗️', description: 'Headers, FAQ, blocks' },
  { key: 'authority', name: 'Authority', icon: '🏆', description: 'Author, E-E-A-T' },
  { key: 'extractability', name: 'Extractability', icon: '🔍', description: 'Readability, clarity' },
  { key: 'technical', name: 'Technical', icon: '⚙️', description: 'AI crawlers, schema' },
] as const;

export function CategoryBreakdown({ breakdown }: CategoryBreakdownProps) {
  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Score Breakdown</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {categories.map(({ key, name, icon, description }) => {
          const data = breakdown[key];
          const pct = (data.score / data.max) * 100;
          
          return (
            <div 
              key={key}
              className="text-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="text-3xl mb-2">{icon}</div>
              <div className="text-sm text-gray-600 mb-1">{name}</div>
              <div className={`text-2xl font-bold ${getScoreColor(data.score, data.max)}`}>
                {data.score}/{data.max}
              </div>
              <div className="text-xs text-gray-500 mt-1">{data.label}</div>
              
              {/* Progress bar */}
              <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all duration-500 ${
                    pct >= 80 ? 'bg-green-500' :
                    pct >= 60 ? 'bg-blue-500' :
                    pct >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
