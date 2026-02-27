'use client';

import { useState } from 'react';
import { Issue } from '@/lib/api';
import { getImpactColor, getImpactIcon } from '@/lib/utils';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface IssuesListProps {
  issues: Issue[];
}

export function IssuesList({ issues }: IssuesListProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (issues.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Issues to Fix</h2>
        <div className="text-center py-8 text-green-600">
          <span className="text-4xl">🎉</span>
          <p className="mt-2 font-medium">No major issues found!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Issues to Fix ({issues.length})</h2>
      
      <div className="space-y-3">
        {issues.map((issue, index) => (
          <div 
            key={index}
            className={`border-l-4 rounded-r-lg ${getImpactColor(issue.impact)} transition-all`}
          >
            <button
              onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
              className="w-full p-4 text-left flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <span className="text-lg">{getImpactIcon(issue.impact)}</span>
                <div>
                  <span className="font-medium">{issue.issue}</span>
                  <span className="ml-2 text-xs uppercase opacity-70">{issue.impact}</span>
                </div>
              </div>
              {expandedIndex === index ? (
                <ChevronUp className="w-5 h-5 opacity-50" />
              ) : (
                <ChevronDown className="w-5 h-5 opacity-50" />
              )}
            </button>
            
            {expandedIndex === index && (
              <div className="px-4 pb-4 space-y-2 animate-fadeIn">
                {issue.current && (
                  <p className="text-sm">
                    <span className="font-medium">Current:</span> {issue.current}
                  </p>
                )}
                {issue.target && (
                  <p className="text-sm">
                    <span className="font-medium">Target:</span> {issue.target}
                  </p>
                )}
                {issue.fix && (
                  <p className="text-sm">
                    <span className="font-medium">Fix:</span> {issue.fix}
                  </p>
                )}
                {issue.predicted_impact && (
                  <p className="text-sm text-green-700 font-medium">
                    📈 Predicted impact: {issue.predicted_impact}
                  </p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
