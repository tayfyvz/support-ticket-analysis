import { TicketForm } from './components/TicketForm/TicketForm';
import { ReadyToAnalyzeGrid } from './components/ReadyToAnalyzeGrid/ReadyToAnalyzeGrid';
import { ProcessingTicketsGrid } from './components/ProcessingTicketsGrid/ProcessingTicketsGrid';
import { AnalyzedTicketsGrid } from './components/AnalyzedTicketsGrid/AnalyzedTicketsGrid';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Support Ticket Analyst</h1>
        <p>AI-powered support ticket management system</p>
      </header>
      <main className="app-main">
        <TicketForm />
        <ReadyToAnalyzeGrid />
        <ProcessingTicketsGrid />
        <AnalyzedTicketsGrid />
      </main>
    </div>
  );
}

export default App;

