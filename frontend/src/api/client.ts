import type { 
  CreateTicketRequest, 
  TicketResponse, 
  TicketListResponse, 
  AnalyzeRequest, 
  AnalysisResponse,
  AnalysisStatusResponse,
  AnalyzedTicketListResponse,
  AnalysisRunListResponse
} from '../types/api';

// Use VITE_API_BASE_URL if set (Docker/production), otherwise empty string for Vite proxy (local dev)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function createTickets(tickets: CreateTicketRequest[]): Promise<TicketResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/tickets`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(tickets),
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to create tickets: ${response.statusText} - ${errorText}`);
  }
  
  return response.json();
}

export async function fetchTickets(options: { page?: number; pageSize?: number; status?: string } = {}): Promise<TicketListResponse> {
  const { page = 1, pageSize = 12, status } = options;
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  
  if (status) {
    params.append('status', status);
  }

  const response = await fetch(`${API_BASE_URL}/api/tickets?${params.toString()}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch tickets: ${response.statusText} - ${errorText}`);
  }

  return response.json();
}

export async function analyzeTickets(request: AnalyzeRequest = {}): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to analyze tickets: ${response.statusText} - ${errorText}`);
  }
  
  return response.json();
}

export async function getLatestAnalysis(): Promise<AnalysisResponse | null> {
  const response = await fetch(`${API_BASE_URL}/api/analysis/latest`);
  
  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    const errorText = await response.text();
    throw new Error(`Failed to fetch analysis: ${response.statusText} - ${errorText}`);
  }
  
  return response.json();
}

export async function fetchAnalyzedTickets(options: { page?: number; pageSize?: number } = {}): Promise<AnalyzedTicketListResponse> {
  const { page = 1, pageSize = 12 } = options;
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });

  const response = await fetch(`${API_BASE_URL}/api/tickets/analyzed?${params.toString()}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch analyzed tickets: ${response.statusText} - ${errorText}`);
  }

  return response.json();
}

export async function getAnalysisStatus(analysisRunId: number): Promise<AnalysisStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analyze/${analysisRunId}/status`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to get analysis status: ${response.statusText} - ${errorText}`);
  }

  return response.json();
}

export async function getActiveAnalysisRuns(): Promise<AnalysisStatusResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/analyze/active`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to get active analysis runs: ${response.statusText} - ${errorText}`);
  }

  return response.json();
}

export async function listAnalysisRuns(options: { page?: number; pageSize?: number } = {}): Promise<AnalysisRunListResponse> {
  const { page = 1, pageSize = 10 } = options;
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });

  const response = await fetch(`${API_BASE_URL}/api/analyze/runs?${params.toString()}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to list analysis runs: ${response.statusText} - ${errorText}`);
  }

  return response.json();
}

export async function getAnalysisRun(analysisRunId: number): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analyze/${analysisRunId}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to get analysis run: ${response.statusText} - ${errorText}`);
  }

  return response.json();
}

