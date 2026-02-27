import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getGradeColor(grade: string): string {
  if (grade.startsWith('A')) return 'text-green-500';
  if (grade === 'B') return 'text-blue-500';
  if (grade === 'C') return 'text-yellow-500';
  if (grade === 'D') return 'text-orange-500';
  return 'text-red-500';
}

export function getScoreColor(score: number, max: number): string {
  const pct = (score / max) * 100;
  if (pct >= 80) return 'text-green-500';
  if (pct >= 60) return 'text-blue-500';
  if (pct >= 40) return 'text-yellow-500';
  return 'text-red-500';
}

export function getImpactColor(impact: string): string {
  switch (impact) {
    case 'critical': return 'bg-red-100 border-red-500 text-red-800';
    case 'high': return 'bg-orange-100 border-orange-500 text-orange-800';
    case 'medium': return 'bg-yellow-100 border-yellow-500 text-yellow-800';
    case 'low': return 'bg-blue-100 border-blue-500 text-blue-800';
    default: return 'bg-gray-100 border-gray-500 text-gray-800';
  }
}

export function getImpactIcon(impact: string): string {
  switch (impact) {
    case 'critical': return '🔴';
    case 'high': return '🟠';
    case 'medium': return '🟡';
    case 'low': return '🟢';
    default: return '⚪';
  }
}
