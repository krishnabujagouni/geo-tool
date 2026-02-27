'use client';

import { getGradeColor } from '@/lib/utils';

interface ScoreCardProps {
  score: number;
  grade: string;
}

export function ScoreCard({ score, grade }: ScoreCardProps) {
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;
  
  const getStrokeColor = () => {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#3b82f6';
    if (score >= 40) return '#eab308';
    return '#ef4444';
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl text-white shadow-xl">
      <div className="relative w-40 h-40">
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="80"
            cy="80"
            r="45"
            stroke="rgba(255,255,255,0.2)"
            strokeWidth="10"
            fill="none"
          />
          {/* Score circle */}
          <circle
            cx="80"
            cy="80"
            r="45"
            stroke={getStrokeColor()}
            strokeWidth="10"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="score-ring"
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-5xl font-bold">{score}</span>
          <span className="text-sm opacity-80">out of 100</span>
        </div>
      </div>
      
      <div className="mt-4 text-center">
        <span className="text-2xl font-semibold">Grade: {grade}</span>
      </div>
    </div>
  );
}
