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
    const csvContent = `title,description
"Unable to Login","I cannot log in to my account. When I enter my credentials, I get an error message saying 'Invalid username or password'. I've tried resetting my password but the email never arrives. This is urgent as I need to access my account for work."
"Billing Discrepancy","I was charged $99.99 for my subscription this month, but my plan should only cost $49.99. I've been on the basic plan for 6 months and this is the first time I've seen this charge. Please investigate and issue a refund."
"Application Crash on Startup","The application crashes immediately when I try to open it. I'm using Windows 11 and the latest version. The error message says 'Application has stopped working'. This started happening after the last update."
"Request for Dark Mode Feature","I would love to see a dark mode option added to the application. I use the app frequently at night and the bright white background is hard on my eyes. Many users have requested this feature."
"Password Reset Email Not Working","I'm trying to reset my password but I'm not receiving the reset email. I've checked my spam folder and tried multiple times. My email address is correct in my account settings."
"Slow Performance on Dashboard","The dashboard takes over 15 seconds to load, and sometimes it times out completely. This happens consistently, especially when viewing reports. It used to load in 2-3 seconds."
"Export Data to Excel","It would be very helpful if users could export their data to Excel format. Currently, we can only export to CSV which doesn't preserve formatting. This would save a lot of time for reporting."
"Email Notifications Not Sending","I'm not receiving email notifications when tickets are assigned to me or when there are updates. I've checked my notification settings and they're all enabled. This is affecting my ability to respond quickly to customers."`;
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

