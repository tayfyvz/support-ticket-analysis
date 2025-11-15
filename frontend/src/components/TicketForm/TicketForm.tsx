import { useState, FormEvent, ChangeEvent, useRef } from 'react';
import { useTicketStore } from '../../store/ticketStore';
import './TicketForm.css';

export function TicketForm() {
  const [title, setTitle] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { createTicket, createTicketsFromCSV, loading, error, clearError } = useTicketStore();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!title.trim() || !description.trim()) {
      return;
    }

    try {
      await createTicket(title.trim(), description.trim());
      setTitle('');
      setDescription('');
      clearError();
    } catch (err) {
      // Error is handled in the store
      console.error('Failed to create ticket:', err);
    }
  };

  const handleTitleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setTitle(e.target.value);
    clearError();
  };

  const handleDescriptionChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setDescription(e.target.value);
    clearError();
  };

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setUploadError('Please upload a CSV file');
      return;
    }

    setUploading(true);
    setUploadError(null);
    clearError();

    try {
      const text = await file.text();
      await createTicketsFromCSV(text);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload CSV file';
      setUploadError(errorMessage);
      console.error('Failed to upload CSV:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadSample = () => {
    const csvContent = 'title,description\n"Login Issue","User cannot log in to the system"\n"Payment Error","Payment processing failed for order #12345"\n"Feature Request","Add dark mode to the application"';
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'sample_tickets.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="ticket-form-container">
      <h2>Create Support Ticket</h2>
      <form onSubmit={handleSubmit} className="ticket-form">
        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={handleTitleChange}
            placeholder="Enter ticket title"
            disabled={loading}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={description}
            onChange={handleDescriptionChange}
            placeholder="Enter ticket description"
            rows={4}
            disabled={loading}
            required
          />
        </div>
        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}
        <button 
          type="submit" 
          disabled={loading || uploading || !title.trim() || !description.trim()} 
          className="submit-button"
        >
          {loading ? 'Creating...' : 'Create Ticket'}
        </button>
      </form>
      
      <div className="csv-upload-section">
        <div className="csv-upload-header">
          <h3>Bulk Upload</h3>
          <button
            type="button"
            onClick={handleDownloadSample}
            className="download-sample-button"
            disabled={loading || uploading}
          >
            Download Sample CSV
          </button>
        </div>
        <div className="csv-upload-controls">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            disabled={loading || uploading}
            style={{ display: 'none' }}
            id="csv-upload-input"
          />
          <label htmlFor="csv-upload-input" className="csv-upload-button">
            {uploading ? 'Uploading...' : 'Upload CSV File'}
          </label>
        </div>
        {uploadError && (
          <div className="error-message" role="alert">
            {uploadError}
          </div>
        )}
        <p className="csv-upload-hint">
          Upload a CSV file with columns: title, description
        </p>
      </div>
    </div>
  );
}

