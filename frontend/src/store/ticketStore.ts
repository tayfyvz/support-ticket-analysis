import { create } from 'zustand';
import { createTickets, fetchTickets, analyzeTickets, getAnalysisStatus } from '../api/client';
import { useAnalyzedTicketStore } from './analyzedTicketStore';
import type { TicketStore, ProcessingTicket } from '../types/store';
import type { TicketResponse } from '../types/api';

export const useTicketStore = create<TicketStore>((set, get) => ({
  tickets: [],
  loading: false,
  error: null,
  page: 1,
  pageSize: 10,
  hasMore: false,
  selectedTicketIds: [],
  processingTickets: [],
  activeAnalysisRuns: {},

  createTicket: async (title: string, description: string): Promise<TicketResponse> => {
    set({ loading: true, error: null });

    try {
      const newTickets = await createTickets([{ title, description }]);
      const createdTicket = newTickets[0];

      set((state) => ({
        tickets: [createdTicket, ...state.tickets].slice(0, state.pageSize),
        loading: false,
        error: null,
        page: 1,
      }));

      // Refresh list to ensure pagination stays consistent
      await get().loadTickets({ page: 1 });

      return createdTicket;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create ticket';
      set({
        loading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  loadTickets: async (options: { page?: number; pageSize?: number } = {}): Promise<void> => {
    const state = get();
    const page = options.page ?? state.page;
    const pageSize = options.pageSize ?? state.pageSize;

    set({ loading: true, error: null });

    try {
      const data = await fetchTickets({ page, pageSize });

      set({
        tickets: data.items,
        loading: false,
        error: null,
        page,
        pageSize,
        hasMore: data.items.length === pageSize,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load tickets';
      set({
        loading: false,
        error: errorMessage,
      });
    }
  },

  nextPage: async (): Promise<void> => {
    const { page, hasMore, loadTickets } = get();
    if (!hasMore) return;
    await loadTickets({ page: page + 1 });
  },

  prevPage: async (): Promise<void> => {
    const { page, loadTickets } = get();
    if (page <= 1) return;
    await loadTickets({ page: page - 1 });
  },

  clearError: (): void => set({ error: null }),

  toggleTicketSelection: (ticketId: number): void => {
    set((state) => {
      const currentSelected = state.selectedTicketIds;
      if (currentSelected.includes(ticketId)) {
        return { selectedTicketIds: currentSelected.filter(id => id !== ticketId) };
      } else {
        return { selectedTicketIds: [...currentSelected, ticketId] };
      }
    });
  },

  clearSelection: (): void => set({ selectedTicketIds: [] }),

  analyzeSelected: async (): Promise<void> => {
    const { selectedTicketIds, tickets } = get();
    if (selectedTicketIds.length === 0) return;
    
    // Get the tickets that are being analyzed
    const ticketsToProcess = tickets.filter(t => selectedTicketIds.includes(t.id));
    
    set({ loading: true, error: null });
    
    try {
      const response = await analyzeTickets({ ticketIds: selectedTicketIds });
      // Remove tickets from ready-to-analyze grid immediately
      set({ 
        tickets: tickets.filter(t => !selectedTicketIds.includes(t.id)),
        selectedTicketIds: []
      });
      // Add tickets to processing list with their analysis run ID
      get().addProcessingTickets(ticketsToProcess, response.id);
      // Start polling for status
      get().startPollingStatus(response.id);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to analyze tickets';
      set({
        loading: false,
        error: errorMessage,
      });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  analyzeAll: async (): Promise<void> => {
    const { tickets } = get();
    
    set({ loading: true, error: null });
    
    try {
      const response = await analyzeTickets({});
      // Remove all tickets from ready-to-analyze grid immediately
      set({ 
        tickets: [],
        selectedTicketIds: []
      });
      // Add tickets to processing list with their analysis run ID
      get().addProcessingTickets([...tickets], response.id);
      // Start polling for status
      get().startPollingStatus(response.id);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to analyze tickets';
      set({
        loading: false,
        error: errorMessage,
      });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  addProcessingTickets: (tickets: TicketResponse[], analysisRunId: number): void => {
    const { processingTickets } = get();
    const newProcessingTickets: ProcessingTicket[] = tickets.map(ticket => ({
      ticket,
      analysisRunId
    }));
    // Append new tickets, avoiding duplicates
    const existingTicketIds = new Set(processingTickets.map(pt => pt.ticket.id));
    const uniqueNewTickets = newProcessingTickets.filter(pt => !existingTicketIds.has(pt.ticket.id));
    set({ processingTickets: [...processingTickets, ...uniqueNewTickets] });
  },

  removeProcessingTickets: (analysisRunId: number): void => {
    const { processingTickets } = get();
    set({ 
      processingTickets: processingTickets.filter(pt => pt.analysisRunId !== analysisRunId)
    });
  },

  startPollingStatus: (analysisRunId: number): void => {
    const { activeAnalysisRuns } = get();
    
    // Don't start polling if already polling this analysis run
    if (activeAnalysisRuns[analysisRunId]) {
      return;
    }
    
    // Poll every 4 seconds
    const pollStatus = async () => {
      try {
        const status = await getAnalysisStatus(analysisRunId);
        
        if (status.status === 'completed') {
          // Analysis completed - stop polling for this run, remove its tickets, refresh grids
          get().stopPollingStatus(analysisRunId);
          get().removeProcessingTickets(analysisRunId);
          await get().loadTickets();
          // Only refresh analyzed tickets once (avoid duplicates from multiple completions)
          await useAnalyzedTicketStore.getState().loadTickets();
        } else if (status.status === 'failed') {
          // Analysis failed - stop polling for this run, remove its tickets, show error
          get().stopPollingStatus(analysisRunId);
          get().removeProcessingTickets(analysisRunId);
          set({ 
            error: 'Analysis failed. Please try again.'
          });
        }
        // If status is 'pending' or 'processing', continue polling
      } catch (error) {
        console.error('Error polling analysis status:', error);
        // Continue polling even on error (might be temporary network issue)
      }
    };
    
    // Poll immediately, then every 4 seconds
    pollStatus();
    const interval = setInterval(pollStatus, 4000);
    
    // Track this polling interval
    set({ activeAnalysisRuns: { ...activeAnalysisRuns, [analysisRunId]: interval } });
  },

  stopPollingStatus: (analysisRunId: number): void => {
    const { activeAnalysisRuns } = get();
    const interval = activeAnalysisRuns[analysisRunId];
    if (interval) {
      clearInterval(interval);
      const { [analysisRunId]: _, ...rest } = activeAnalysisRuns;
      set({ activeAnalysisRuns: rest });
    }
  },

  stopAllPolling: (): void => {
    const { activeAnalysisRuns } = get();
    Object.values(activeAnalysisRuns).forEach((interval) => clearInterval(interval));
    set({ activeAnalysisRuns: {} });
  },
}));

