export interface TicketResponse {
  id: number;
  title: string;
  description: string;
  created_at: string; // ISO date string
  status: string; // "pending" | "processing" | "analyzed" | "failed"
}

export interface TicketListResponse {
  items: TicketResponse[];
  page: number;
  page_size: number;
}

export interface CreateTicketRequest {
  title: string;
  description: string;
}

export interface AnalyzeRequest {
  ticketIds?: number[];
}

export interface TicketAnalysis {
  id: number;
  ticket_id: number;
  category: string;
  priority: 'low' | 'medium' | 'high';
  notes: string | null;
  ticket?: TicketResponse;
}

export interface AnalysisResponse {
  id: number;
  created_at: string;
  summary: string | null;
  status: string;
  ticket_analyses: TicketAnalysis[];
}

export interface AnalysisStatusResponse {
  analysis_run_id: number;
  status: string; // "pending" | "processing" | "completed" | "failed"
  ticket_ids: number[];
}

export interface AnalyzedTicketResponse {
  id: number; // ticket id
  analysis_id: number; // ticket_analysis id (for unique key)
  title: string;
  description: string;
  priority: string;
  category: string;
  notes: string | null;
}

export interface AnalyzedTicketListResponse {
  items: AnalyzedTicketResponse[];
  page: number;
  page_size: number;
}

