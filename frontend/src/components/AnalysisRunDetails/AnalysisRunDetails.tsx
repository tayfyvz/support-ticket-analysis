import type { AnalysisResponse } from '../../types/api';
import './AnalysisRunDetails.css';

interface AnalysisRunDetailsProps {
  runId: number;
  details: AnalysisResponse | null;
  loading: boolean;
  onClose: () => void;
}

export function AnalysisRunDetails({ runId, details, loading, onClose }: AnalysisRunDetailsProps) {
  const getPriorityClass = (priority: string) => {
    const priorityLower = priority.toLowerCase();
    if (priorityLower === 'high') return 'priority-high';
    if (priorityLower === 'medium') return 'priority-medium';
    return 'priority-low';
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Analysis Run #{runId}</h2>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        <div className="modal-body">
          {loading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <div className="loading-text">Loading details...</div>
            </div>
          )}

          {!loading && details && (
            <>
              <div className="run-info">
                <div className="info-item">
                  <span className="info-label">Created:</span>
                  <span className="info-value">
                    {new Date(details.created_at).toLocaleString()}
                  </span>
                </div>
                {details.summary && (
                  <div className="info-item">
                    <span className="info-label">Summary:</span>
                    <span className="info-value">{details.summary}</span>
                  </div>
                )}
                <div className="info-item">
                  <span className="info-label">Tickets Analyzed:</span>
                  <span className="info-value">{details.ticket_analyses.length}</span>
                </div>
              </div>

              {details.ticket_analyses.length > 0 ? (
                <div className="tickets-list">
                  <h3>Tickets</h3>
                  <div className="ticket-details-table">
                    <div className="ticket-details-table-wrapper">
                      <div className="ticket-details-header">
                        <span>Title</span>
                        <span>Description</span>
                        <span>Category</span>
                        <span>Priority</span>
                        <span>Notes</span>
                      </div>
                      <div className="ticket-details-body">
                        {details.ticket_analyses.map((analysis) => (
                          <div key={analysis.id} className="ticket-details-row">
                            <span className="ticket-title">
                              {analysis.ticket?.title || 'N/A'}
                            </span>
                            <span className="ticket-description">
                              {analysis.ticket?.description || 'N/A'}
                            </span>
                            <span className="ticket-category">
                              {analysis.category}
                            </span>
                            <span className={`ticket-priority ${getPriorityClass(analysis.priority)}`}>
                              {analysis.priority}
                            </span>
                            <span className="ticket-notes">
                              {analysis.notes || '-'}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="no-tickets">No tickets analyzed yet.</div>
              )}
            </>
          )}

          {!loading && !details && (
            <div className="error-message">Failed to load analysis run details.</div>
          )}
        </div>
      </div>
    </div>
  );
}

