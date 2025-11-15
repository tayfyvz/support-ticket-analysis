import { useTicketStore } from '../../store/ticketStore';
import './ProcessingTicketsGrid.css';

export function ProcessingTicketsGrid() {
  const processingTickets = useTicketStore((state) => state.processingTickets);

  // Don't render if no tickets are processing
  if (processingTickets.length === 0) {
    return null;
  }

  return (
    <section className="processing-tickets-section">
      <div className="section-header">
        <div>
          <h2>Processing Tickets</h2>
          <p>
            Analyzing {processingTickets.length} ticket{processingTickets.length !== 1 ? 's' : ''}...
          </p>
        </div>
      </div>
      <div className="ticket-grid-container">
        <div className="ticket-grid-table" role="table">
          <div className="ticket-grid-header" role="row">
            <span role="columnheader">Status</span>
            <span role="columnheader">Title</span>
            <span role="columnheader">Description</span>
            <span role="columnheader">Created</span>
          </div>
          <div className="ticket-grid-body">
            {processingTickets.map((processingTicket) => (
              <div key={`${processingTicket.analysisRunId}-${processingTicket.ticket.id}`} className="ticket-grid-row processing-row" role="row">
                <span role="cell" className="ticket-status">
                  <div className="processing-spinner"></div>
                  <span className="processing-text">Processing</span>
                </span>
                <span role="cell" className="ticket-title">
                  {processingTicket.ticket.title}
                </span>
                <span role="cell" className="ticket-description">
                  {processingTicket.ticket.description}
                </span>
                <span role="cell" className="ticket-created">
                  {new Date(processingTicket.ticket.created_at).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

