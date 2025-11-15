import { useEffect, ChangeEvent } from 'react';
import { useTicketStore } from '../../store/ticketStore';
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

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  const handleSelectAll = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      tickets.forEach(t => {
        if (!selectedTicketIds.includes(t.id)) {
          toggleTicketSelection(t.id);
        }
      });
    } else {
      tickets.forEach(t => {
        if (selectedTicketIds.includes(t.id)) {
          toggleTicketSelection(t.id);
        }
      });
    }
  };

  const renderContent = () => {
    if (loading) {
      return <div className="grid-status">Loading tickets...</div>;
    }

    if (error) {
      return <div className="grid-status grid-error">{error}</div>;
    }

    if (!tickets.length) {
      return <div className="grid-status">No ready-to-analyze tickets yet.</div>;
    }

    const allSelected = tickets.length > 0 && tickets.every(t => selectedTicketIds.includes(t.id));

    return (
      <div className="ticket-grid-table" role="table">
        <div className="ticket-grid-header" role="row">
          <span role="columnheader">
            <input
              type="checkbox"
              aria-label="Select all"
              checked={allSelected}
              onChange={handleSelectAll}
            />
          </span>
          <span role="columnheader">Title</span>
          <span role="columnheader">Description</span>
          <span role="columnheader">Created</span>
        </div>
        <div className="ticket-grid-body">
          {tickets.map((ticket) => (
            <div key={ticket.id} className="ticket-grid-row" role="row">
              <span role="cell" className="ticket-checkbox">
                <input
                  type="checkbox"
                  checked={selectedTicketIds.includes(ticket.id)}
                  onChange={() => toggleTicketSelection(ticket.id)}
                  aria-label={`Select ticket ${ticket.id}`}
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
    );
  };

  return (
    <section className="unanalyzed-section">
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

