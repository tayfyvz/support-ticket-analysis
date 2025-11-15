import { TicketResponse } from './api';

export interface ProcessingTicket {
  ticket: TicketResponse;
  analysisRunId: number;
}

export interface TicketStore {
  // State
  tickets: TicketResponse[];
  loading: boolean;
  error: string | null;
  page: number;
  pageSize: number;
  hasMore: boolean;
  selectedTicketIds: number[];
  processingTickets: ProcessingTicket[];
  activeAnalysisRuns: Record<number, NodeJS.Timeout>; // Record of analysisRunId to polling interval

  // Actions
  createTicket: (title: string, description: string) => Promise<TicketResponse>;
  loadTickets: (options?: { page?: number; pageSize?: number }) => Promise<void>;
  nextPage: () => Promise<void>;
  prevPage: () => Promise<void>;
  toggleTicketSelection: (ticketId: number) => void;
  clearSelection: () => void;
  analyzeSelected: () => Promise<void>;
  analyzeAll: () => Promise<void>;
  clearError: () => void;
  addProcessingTickets: (tickets: TicketResponse[], analysisRunId: number) => void;
  removeProcessingTickets: (analysisRunId: number) => void;
  startPollingStatus: (analysisRunId: number) => void;
  stopPollingStatus: (analysisRunId: number) => void;
  stopAllPolling: () => void;
}

