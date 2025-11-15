import { useState, FormEvent, ChangeEvent } from 'react';
import { useTicketStore } from '../../store/ticketStore';
import './TicketForm.css';

export function TicketForm() {
  const [title, setTitle] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const { createTicket, loading, error, clearError } = useTicketStore();

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
          disabled={loading || !title.trim() || !description.trim()} 
          className="submit-button"
        >
          {loading ? 'Creating...' : 'Create Ticket'}
        </button>
      </form>
    </div>
  );
}

