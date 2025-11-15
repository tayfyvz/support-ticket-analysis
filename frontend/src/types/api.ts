export interface TicketResponse {
  id: number;
  title: string;
  description: string;
  created_at: string; // ISO date string
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
  ticket_analyses: TicketAnalysis[];
}

