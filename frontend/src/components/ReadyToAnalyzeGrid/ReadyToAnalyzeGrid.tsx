import { useEffect, useState, ChangeEvent } from 'react';
import { useTicketStore } from '../../store/ticketStore';
import type { TicketResponse } from '../../types/api';
import './ReadyToAnalyzeGrid.css';

export function ReadyToAnalyzeGrid() {
  const tickets = useTicketStore((state) => state.tickets);
  const loading = useTicketStore((state) => state.loading);
  const error = useTicketStore((state) => state.error);
  const page = useTicketStore((state) => state.page);
  const hasMore = useTicketStore((state) => state.hasMore);
  const selectedTicketIds = useTicketStore((state) => state.selectedTicketIds);
  const loadTickets = useTicketStore((state) => state.loadTickets);
  const nextPage = useTicketStore((state) => state.nextPage);
  const prevPage = useTicketStore((state) => state.prevPage);
  const toggleTicketSelection = useTicketStore((state) => state.toggleTicketSelection);
  const analyzeSelected = useTicketStore((state) => state.analyzeSelected);
  const analyzeAll = useTicketStore((state) => state.analyzeAll);

  // Keep previous tickets visible during loading to prevent scroll jump
  const [displayTickets, setDisplayTickets] = useState<TicketResponse[]>(tickets);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  // Update display tickets only when loading completes
  // This keeps the old tickets visible during loading to prevent scroll jump
  useEffect(() => {
    if (!loading) {
      // Update display tickets when loading completes
      setDisplayTickets(tickets);
    }
    // When loading starts, displayTickets remains unchanged (showing previous tickets)
  }, [tickets, loading]);

  const handleSelectAll = (e: ChangeEvent<HTMLInputElement>) => {
    const ticketsToProcess = displayTickets.length > 0 ? displayTickets : tickets;
    if (e.target.checked) {
      ticketsToProcess.forEach(t => {
        if (!selectedTicketIds.includes(t.id)) {
          toggleTicketSelection(t.id);
        }
      });
    } else {
      ticketsToProcess.forEach(t => {
        if (selectedTicketIds.includes(t.id)) {
          toggleTicketSelection(t.id);
        }
      });
    }
  };

  const renderContent = () => {
    // Show error state
    if (error && !displayTickets.length) {
      return <div className="grid-status grid-error">{error}</div>;
    }

    // Show empty state only when not loading and no tickets
    if (!loading && !displayTickets.length && !tickets.length) {
      return <div className="grid-status">No ready-to-analyze tickets yet.</div>;
    }

    // Use displayTickets to maintain content during loading
    const ticketsToShow = displayTickets.length > 0 ? displayTickets : tickets;
    const allSelected = ticketsToShow.length > 0 && ticketsToShow.every(t => selectedTicketIds.includes(t.id));

    return (
      <div className="ticket-grid-container">
        <div className="ticket-grid-table" role="table">
          <div className="ticket-grid-header" role="row">
            <span role="columnheader">
              <input
                type="checkbox"
                aria-label="Select all"
                checked={allSelected}
                onChange={handleSelectAll}
                disabled={loading}
              />
            </span>
            <span role="columnheader">Title</span>
            <span role="columnheader">Description</span>
            <span role="columnheader">Created</span>
          </div>
          <div className="ticket-grid-body">
            {ticketsToShow.map((ticket) => (
              <div key={ticket.id} className="ticket-grid-row" role="row">
                <span role="cell" className="ticket-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedTicketIds.includes(ticket.id)}
                    onChange={() => toggleTicketSelection(ticket.id)}
                    aria-label={`Select ticket ${ticket.id}`}
                    disabled={loading}
                  />
                </span>
                <span role="cell" className="ticket-title">
                  {ticket.title}
                </span>
                <span role="cell" className="ticket-description">
                  {ticket.description}
                </span>
                <span role="cell" className="ticket-created">
                  {new Date(ticket.created_at).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <div className="loading-text">Loading tickets...</div>
          </div>
        )}
        {error && displayTickets.length > 0 && (
          <div className="grid-error-message">{error}</div>
        )}
      </div>
    );
  };

  return (
    <section className="ready-to-analyze-section">
      <div className="section-header">
        <div>
          <h2>Ready to Analyze</h2>
          <p>
            Tickets awaiting analysis
            {selectedTicketIds.length > 0 && (
              <span className="selection-count"> ({selectedTicketIds.length} selected)</span>
            )}
          </p>
        </div>
        <div className="header-actions">
          <div className="analyze-buttons">
            <button
              type="button"
              onClick={analyzeSelected}
              disabled={loading || selectedTicketIds.length === 0}
              className="analyze-button analyze-selected"
            >
              Analyze Selected
            </button>
            <button
              type="button"
              onClick={analyzeAll}
              disabled={loading || tickets.length === 0}
              className="analyze-button analyze-all"
            >
              Analyze All
            </button>
          </div>
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

