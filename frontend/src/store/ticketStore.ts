import { create } from 'zustand';
import { createTickets, fetchTickets } from '../api/client';
import type { TicketStore } from '../types/store';
import type { TicketResponse } from '../types/api';

export const useTicketStore = create<TicketStore>((set, get) => ({
  tickets: [],
  loading: false,
  error: null,
  page: 1,
  pageSize: 10,
  hasMore: false,
  selectedTicketIds: [],

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
    const { selectedTicketIds } = get();
    if (selectedTicketIds.length === 0) return;
    
    // TODO: Implement analyze API call
    console.log('Analyzing selected tickets:', selectedTicketIds);
    // After analysis, clear selection and refresh tickets
    set({ selectedTicketIds: [] });
    await get().loadTickets();
  },

  analyzeAll: async (): Promise<void> => {
    // TODO: Implement analyze all API call
    console.log('Analyzing all tickets');
    // After analysis, clear selection and refresh tickets
    set({ selectedTicketIds: [] });
    await get().loadTickets();
  },
}));

