export interface AnalysisResponse {
  success: boolean;
  data?: {
    severity: string;
    confidence: number;
    severity_scores: Record<string, number>;
    processing_time: number;
  };
  error?: string;
}
