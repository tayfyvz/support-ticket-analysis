import { useEffect, useState, useCallback, useRef } from 'react';
import { listAnalysisRuns, getAnalysisRun } from '../../api/client';
import type { AnalysisRunListItem, AnalysisResponse } from '../../types/api';
import { AnalysisRunDetails } from '../AnalysisRunDetails/AnalysisRunDetails';
import './AnalysisRunsGrid.css';

export function AnalysisRunsGrid() {
  const [runs, setRuns] = useState<AnalysisRunListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);
  const [total, setTotal] = useState<number>(0);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [selectedRunDetails, setSelectedRunDetails] = useState<AnalysisResponse | null>(null);
  const [loadingDetails, setLoadingDetails] = useState<boolean>(false);
  const pageRef = useRef(page);
  
  // Keep ref in sync with state
  useEffect(() => {
    pageRef.current = page;
  }, [page]);

  const loadRuns = useCallback(async (pageNum?: number) => {
    const targetPage = pageNum ?? pageRef.current;
    setLoading(true);
    setError(null);
    try {
      const data = await listAnalysisRuns({ page: targetPage, pageSize });
      setRuns(data.items);
      setPage(data.page);
      setTotal(data.total);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load analysis runs';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  useEffect(() => {
    loadRuns();
  }, [loadRuns]);

  // Listen for analysis completion events to refresh the grid
  useEffect(() => {
    const handleAnalysisCompleted = () => {
      // Reload the current page to show updated analysis run status
      loadRuns();
    };

    window.addEventListener('analysisCompleted', handleAnalysisCompleted);
    return () => {
      window.removeEventListener('analysisCompleted', handleAnalysisCompleted);
    };
  }, [loadRuns]);

  const handleRunClick = async (runId: number) => {
    setSelectedRunId(runId);
    setLoadingDetails(true);
    try {
      const details = await getAnalysisRun(runId);
      setSelectedRunDetails(details);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load analysis run details';
      setError(errorMessage);
      setSelectedRunId(null);
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleCloseDetails = () => {
    setSelectedRunId(null);
    setSelectedRunDetails(null);
  };

  const hasMore = page * pageSize < total;
  const hasPrev = page > 1;

  return (
    <>
      <section className="analysis-runs-section">
        <div className="section-header">
          <div>
            <h2>Analysis Runs</h2>
            <p>View all analysis runs and their details</p>
          </div>
          <div className="header-actions">
            <div className="pagination-controls">
              <button
                type="button"
                onClick={() => loadRuns(page - 1)}
                disabled={loading || !hasPrev}
              >
                Previous
              </button>
              <span className="page-indicator">Page {page}</span>
              <button
                type="button"
                onClick={() => loadRuns(page + 1)}
                disabled={loading || !hasMore}
              >
                Next
              </button>
            </div>
          </div>
        </div>

        {error && !runs.length && (
          <div className="grid-status grid-error">{error}</div>
        )}

        {!loading && !runs.length && !error && (
          <div className="grid-status">No analysis runs yet.</div>
        )}

        {runs.length > 0 && (
          <div className="ticket-grid-container">
            <div className="ticket-grid-table" role="table">
              <div className="ticket-grid-header" role="row">
                <span role="columnheader">ID</span>
                <span role="columnheader">Created</span>
                <span role="columnheader">Tickets</span>
                <span role="columnheader">Summary</span>
                <span role="columnheader"></span>
              </div>
              <div className="ticket-grid-body">
                {runs.map((run) => (
                  <div
                    key={run.id}
                    className="ticket-grid-row clickable-row"
                    role="row"
                    onClick={() => handleRunClick(run.id)}
                    title="Click to view details"
                  >
                    <span role="cell" className="run-id">
                      #{run.id}
                    </span>
                    <span role="cell" className="run-created">
                      {new Date(run.created_at).toLocaleString()}
                    </span>
                    <span role="cell" className="run-ticket-count">
                      {run.ticket_count}
                    </span>
                    <span role="cell" className="run-summary">
                      {run.summary || '-'}
                    </span>
                    <span role="cell" className="run-action">
                      <span className="view-details-text">View Details</span>
                      <span className="arrow-icon">→</span>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <div className="loading-text">Loading analysis runs...</div>
          </div>
        )}
      </section>

      {selectedRunId && (
        <AnalysisRunDetails
          runId={selectedRunId}
          details={selectedRunDetails}
          loading={loadingDetails}
          onClose={handleCloseDetails}
        />
      )}
    </>
  );
}

