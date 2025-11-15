import { useEffect, useState } from 'react';
import { useAnalyzedTicketStore } from '../../store/analyzedTicketStore';
import type { AnalyzedTicketResponse } from '../../types/api';
import './AnalyzedTicketsGrid.css';

export function AnalyzedTicketsGrid() {
  const tickets = useAnalyzedTicketStore((state) => state.tickets);
  const loading = useAnalyzedTicketStore((state) => state.loading);
  const error = useAnalyzedTicketStore((state) => state.error);
  const page = useAnalyzedTicketStore((state) => state.page);
  const hasMore = useAnalyzedTicketStore((state) => state.hasMore);
  const loadTickets = useAnalyzedTicketStore((state) => state.loadTickets);
  const nextPage = useAnalyzedTicketStore((state) => state.nextPage);
  const prevPage = useAnalyzedTicketStore((state) => state.prevPage);

  // Keep previous tickets visible during loading to prevent scroll jump
  const [displayTickets, setDisplayTickets] = useState<AnalyzedTicketResponse[]>(tickets);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  // Update display tickets only when loading completes
  useEffect(() => {
    if (!loading) {
      setDisplayTickets(tickets);
    }
  }, [tickets, loading]);

  const getPriorityClass = (priority: string) => {
    const priorityLower = priority.toLowerCase();
    if (priorityLower === 'high') return 'priority-high';
    if (priorityLower === 'medium') return 'priority-medium';
    return 'priority-low';
  };

  const renderContent = () => {
    // Show error state
    if (error && !displayTickets.length) {
      return <div className="grid-status grid-error">{error}</div>;
    }

    // Show empty state only when not loading and no tickets
    if (!loading && !displayTickets.length && !tickets.length) {
      return <div className="grid-status">No analyzed tickets yet.</div>;
    }

    // Use displayTickets to maintain content during loading
    const ticketsToShow = displayTickets.length > 0 ? displayTickets : tickets;

    return (
      <div className="ticket-grid-container">
        <div className="ticket-grid-table" role="table">
          <div className="ticket-grid-header" role="row">
            <span role="columnheader">Title</span>
            <span role="columnheader">Description</span>
            <span role="columnheader">Priority</span>
            <span role="columnheader">Category</span>
            <span role="columnheader">Notes</span>
          </div>
          <div className="ticket-grid-body">
            {ticketsToShow.map((ticket) => (
              <div key={ticket.analysis_id} className="ticket-grid-row" role="row">
                <span role="cell" className="ticket-title">
                  {ticket.title}
                </span>
                <span role="cell" className="ticket-description">
                  {ticket.description}
                </span>
                <span role="cell" className={`ticket-priority ${getPriorityClass(ticket.priority)}`}>
                  {ticket.priority}
                </span>
                <span role="cell" className="ticket-category">
                  {ticket.category}
                </span>
                <span role="cell" className="ticket-notes">
                  {ticket.notes || '-'}
                </span>
              </div>
            ))}
          </div>
        </div>
        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <div className="loading-text">Loading analyzed tickets...</div>
          </div>
        )}
        {error && displayTickets.length > 0 && (
          <div className="grid-error-message">{error}</div>
        )}
      </div>
    );
  };

  return (
    <section className="analyzed-tickets-section">
      <div className="section-header">
        <div>
          <h2>Analyzed Tickets</h2>
          <p>Tickets that have been analyzed</p>
        </div>
        <div className="header-actions">
          <div className="pagination-controls">
            <button
              type="button"
              onClick={prevPage}
              disabled={loading || page <= 1}
            >
              Previous
            </button>
            <span className="page-indicator">Page {page}</span>
            <button
              type="button"
              onClick={nextPage}
              disabled={loading || !hasMore}
            >
              Next
            </button>
          </div>
        </div>
      </div>
      {renderContent()}
    </section>
  );
}

