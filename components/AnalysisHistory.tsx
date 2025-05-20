"use client";

import React from 'react';
import { Info, AlertTriangle } from 'lucide-react';
import { Tooltip } from './ui/tooltip';

interface AnalysisHistoryProps {
  history: Array<{
    id: string;
    date: string;
    severity: string;
    confidence: number;
    severity_scores: Record<string, number>;
  }>;
}

const severityColors: Record<string, string> = {
  'No DR': 'bg-green-100 text-green-800',
  'Mild DR': 'bg-yellow-100 text-yellow-800',
  'Moderate DR': 'bg-orange-100 text-orange-800',
  'Severe DR': 'bg-red-100 text-red-800',
  'Proliferative DR': 'bg-red-200 text-red-900'
};

export function AnalysisHistory({ history }: AnalysisHistoryProps) {
  return (
    <section className="mt-8 bg-white p-8 rounded-lg shadow-lg">
      <h2 className="text-xl font-semibold mb-6">Analysis History</h2>
      <div className="analysis-grid">
        {history.map((result) => (
          <article 
            key={result.id}
            className="p-4 border rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start mb-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${severityColors[result.severity]}`}>
                {result.severity}
              </span>
              <Tooltip tooltip={result.date}>
                <Info className="w-4 h-4 text-gray-400" />
              </Tooltip>
            </div>
            
            <div className="mt-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Confidence:</span>
                <span className="text-sm font-medium">
                  {result.confidence.toFixed(1)}%
                </span>
              </div>
              
              {result.confidence < 50 && (
                <div className="mt-2 flex items-start gap-1.5 text-yellow-700">
                  <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span className="text-xs">Low confidence prediction</span>
                </div>
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

