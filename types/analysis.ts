export interface AnalysisData {
  severity: string;
  confidence: number;
  severity_scores: Record<string, number>;
  processing_time: number;
}

export interface AnalysisResponse {
  success: boolean;
  data?: AnalysisData;
  error?: string;
}
