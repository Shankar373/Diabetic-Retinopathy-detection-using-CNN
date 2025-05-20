export interface AnalysisResult {
  drScore: number;
  confidence: number;
  severity: 'None' | 'Mild' | 'Moderate' | 'Severe' | 'Proliferative';
}

export interface ApiResponse {
  success: boolean;
  result?: AnalysisResult;
  error?: string;
}
