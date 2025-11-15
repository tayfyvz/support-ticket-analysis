import { TicketResponse } from './api';

export interface TicketStore {
  // State
  tickets: TicketResponse[];
  loading: boolean;
  error: string | null;
  page: number;
  pageSize: number;
  hasMore: boolean;
  selectedTicketIds: number[];

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
}

