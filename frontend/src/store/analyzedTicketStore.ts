import { create } from 'zustand';
import { fetchAnalyzedTickets } from '../api/client';
import type { AnalyzedTicketResponse } from '../types/api';

interface AnalyzedTicketStore {
  // State
  tickets: AnalyzedTicketResponse[];
  loading: boolean;
  error: string | null;
  page: number;
  pageSize: number;
  hasMore: boolean;

  // Actions
  loadTickets: (options?: { page?: number; pageSize?: number }) => Promise<void>;
  nextPage: () => Promise<void>;
  prevPage: () => Promise<void>;
  clearError: () => void;
}

export const useAnalyzedTicketStore = create<AnalyzedTicketStore>((set, get) => ({
  tickets: [],
  loading: false,
  error: null,
  page: 1,
  pageSize: 10,
  hasMore: false,

  loadTickets: async (options: { page?: number; pageSize?: number } = {}): Promise<void> => {
    const state = get();
    const page = options.page ?? state.page;
    const pageSize = options.pageSize ?? state.pageSize;

    set({ loading: true, error: null });

    try {
      const data = await fetchAnalyzedTickets({ page, pageSize });

      set({
        tickets: data.items,
        loading: false,
        error: null,
        page,
        pageSize,
        hasMore: data.items.length === pageSize,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load analyzed tickets';
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
}));

