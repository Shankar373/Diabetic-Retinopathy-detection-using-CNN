import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json(
        { success: false, error: 'No file provided' },
        { status: 400 }
      );
    }

    const pythonApiUrl = process.env.NEXT_PUBLIC_PYTHON_API_URL;
    if (!pythonApiUrl) {
      throw new Error('Python API URL not configured');
    }

    console.log('Forwarding request to Python API:', `${pythonApiUrl}/predict`);
    
    const pythonFormData = new FormData();
    pythonFormData.append('file', file);

    const response = await fetch(`${pythonApiUrl}/predict`, {
      method: 'POST',
      body: pythonFormData,
    });

    if (!response.ok) {
      throw new Error(`Python API error: ${response.statusText}`);
    }

    const result = await response.json();

    return NextResponse.json({
      success: true,
      data: {
        severity: result.severity || 'Unknown',
        confidence: result.confidence || 0,
        severity_scores: result.severity_scores || {},
        processing_time: result.processing_time || 0
      }
    });

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Internal server error'
      },
      { status: 500 }
    );
  }
}
