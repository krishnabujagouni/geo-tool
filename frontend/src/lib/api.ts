const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CategoryScore {
  score: number;
  max: number;
  label: string;
}

export interface Issue {
  category: string;
  issue: string;
  impact: 'critical' | 'high' | 'medium' | 'low';
  source?: 'seo' | 'geo';
  current?: string;
  target?: string;
  fix?: string;
  predicted_impact?: string;
}

export interface Recommendation {
  priority: number;
  title: string;
  description: string;
  actions: string[];
  impact: string;
}

export interface CombinedResult {
  url: string;
  combined_score: number;
  combined_grade: string;
  seo: {
    score: number;
    grade: string;
    breakdown: {
      meta_tags: CategoryScore;
      content_quality: CategoryScore;
      structure: CategoryScore;
      technical: CategoryScore;
      performance: CategoryScore;
    };
    issues: Issue[];
  };
  geo: {
    score: number;
    grade: string;
    breakdown: {
      citeability: CategoryScore;
      structure: CategoryScore;
      authority: CategoryScore;
      extractability: CategoryScore;
      technical: CategoryScore;
    };
    issues: Issue[];
  };
  unified_issues: Issue[];
  unified_quick_wins: string[];
  recommendations: Recommendation[];
  word_count: number;
  metadata?: {
    title?: string;
    description?: string;
  };
}

export interface FAQResult {
  faqs: { question: string; answer: string }[];
  schema_markup: string;
  html: string;
  ai_generated: boolean;
  error?: string;
}

export interface RewriteResult {
  original: string;
  rewritten: string | null;
  changes: { type: string; description: string }[];
  predicted_score_increase: number;
  error?: string;
}

// Combined SEO + GEO Analysis
export async function analyzeUrl(url: string): Promise<CombinedResult> {
  const response = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze URL');
  }
  
  return response.json();
}

// Generate FAQ
export async function generateFAQ(content: string, numQuestions: number = 5): Promise<FAQResult> {
  const response = await fetch(`${API_URL}/api/generate/faq`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, num_questions: numQuestions }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate FAQ');
  }
  
  return response.json();
}

// Rewrite content
export async function rewriteContent(
  content: string, 
  improvements: string[],
  issues?: Issue[]
): Promise<RewriteResult> {
  const response = await fetch(`${API_URL}/api/rewrite`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, improvements, issues }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to rewrite content');
  }
  
  return response.json();
}

// Check API health
export async function checkHealth(): Promise<{ status: string; ai_enabled: boolean }> {
  const response = await fetch(`${API_URL}/health`);
  return response.json();
}
