'use client';

interface QuickWinsProps {
  quickWins: string[];
}

export function QuickWins({ quickWins }: QuickWinsProps) {
  if (quickWins.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">✅ Quick Wins</h2>
      
      <div className="space-y-2">
        {quickWins.map((win, index) => (
          <div 
            key={index}
            className="flex items-start gap-3 p-3 bg-green-50 border-l-4 border-green-500 rounded-r-lg"
          >
            <span className="text-green-600">✨</span>
            <span className="text-sm text-green-800">{win}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
