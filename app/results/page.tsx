"use client";
import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { FileText, Download, Filter } from 'lucide-react';
import { format } from 'date-fns';
import { Tooltip } from '@/components/ui/tooltip';

interface AnalysisResult {
  id: string;
  date: string;
  severity: string;
  confidence: number;
  image_url: string;
  severity_scores: Record<string, number>;
}

export default function ResultsPage() {
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [filter, setFilter] = useState('all');
  
  useEffect(() => {
    // Load results from local storage or API
    const loadResults = async () => {
      try {
        const response = await fetch('/api/results');
        const data = await response.json();
        setResults(data);
      } catch (error) {
        console.error('Failed to load results:', error);
      }
    };
    loadResults();
  }, []);

  const filteredResults = results.filter(result => {
    if (filter === 'all') return true;
    return result.severity.toLowerCase() === filter;
  });

  const handleExport = () => {
    const csv = results.map(r => Object.values(r).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dr-analysis-${format(new Date(), 'yyyy-MM-dd')}.csv`;
    a.click();
  };

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <FileText className="w-8 h-8" />
            Analysis Results
          </h1>
          <div className="flex gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-500" />
              <select
                aria-label="Filter results"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="border rounded-md p-2"
              >
                <option value="all">All Results</option>
                <option value="no dr">No DR</option>
                <option value="mild">Mild DR</option>
                <option value="moderate">Moderate DR</option>
                <option value="severe">Severe DR</option>
              </select>
            </div>
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              <Download className="w-4 h-4" />
              Export Results
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredResults.map((result) => (
            <div key={result.id} className="bg-white rounded-lg shadow p-4">
              <div className="relative h-48 mb-4">
                <Image
                  src={result.image_url}
                  alt="Retinal scan"
                  fill
                  className="object-cover rounded-md"
                />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">
                    {format(new Date(result.date), 'PPp')}
                  </span>
                  <Tooltip tooltip={`Confidence: ${result.confidence}%`}>
                    <span className={`px-2 py-1 rounded-full text-sm font-medium
                      ${result.severity === 'No DR' ? 'bg-green-100 text-green-800' : 
                        result.severity === 'Mild DR' ? 'bg-yellow-100 text-yellow-800' :
                        result.severity === 'Moderate DR' ? 'bg-orange-100 text-orange-800' :
                        'bg-red-100 text-red-800'}`}
                    >
                      {result.severity}
                    </span>
                  </Tooltip>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
