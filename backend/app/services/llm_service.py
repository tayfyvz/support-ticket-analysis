"""LLM service for ticket analysis using LangGraph."""

import os
from typing import Dict, List, Literal, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from app.prompts.ticket_analysis import CLASSIFY_PROMPT_TEMPLATE, SUMMARY_PROMPT_TEMPLATE

# Load environment variables from .env file (if it exists)
# This works for local development. In Docker, environment variables should be
# set via docker-compose.yml or Docker environment variables.
load_dotenv()  # Will search for .env in current and parent directories


# Pydantic model for structured output (ticket classification)
class TicketClassification(BaseModel):
    """The classification for a single support ticket."""

    category: Literal["billing", "bug", "feature_request", "support", "technical", "account"] = Field(
        ...,
        description="The assigned category. Must be one of: billing, bug, feature_request, support, technical, account"
    )
    priority: Literal["low", "medium", "high"] = Field(
        ...,
        description="The assigned priority. Must be one of: low, medium, high"
    )
    notes: str | None = Field(
        default=None,
        description="Optional notes or additional insights about the ticket. Leave empty if no notes are needed."
    )


# Pydantic model for structured summary output
class BatchSummary(BaseModel):
    """Executive summary of a batch of processed tickets."""

    summary: str = Field(
        ...,
        description="A concise, one-paragraph executive summary of the batch of processed tickets. Highlight major themes, common categories, or urgent (high-priority) issues."
    )


# Graph state definition
class TicketTriageState(TypedDict):
    """
    Represents the state of the ticket processing graph.

    Attributes:
        input_tickets: The initial list of tickets to process.
        processed_tickets: The list of tickets *after* classification.
        batch_summary: The final summary of all tickets.
    """

    input_tickets: List[Dict]
    processed_tickets: List[Dict]
    batch_summary: str


class LLMService:
    """Service for LLM-based ticket analysis."""

    def __init__(self):
        """Initialize the LLM service with API key from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set in environment variables. "
                "Please set it in your .env file. See backend/ENV_SETUP.md for instructions."
            )
        
        # Initialize the LLM with gpt-4o-mini for speed and structured output
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key
        )
        self._graph = None

    def _build_graph(self) -> StateGraph:
        """Build and compile the LangGraph for ticket processing."""
        if self._graph is not None:
            return self._graph

        builder = StateGraph(TicketTriageState)

        # Add the "Map" node
        builder.add_node("process_ticket_batch", self._process_ticket_batch)

        # Add the "Reduce" node
        builder.add_node("generate_batch_summary", self._generate_batch_summary)

        # Define the flow
        builder.set_entry_point("process_ticket_batch")
        builder.add_edge("process_ticket_batch", "generate_batch_summary")
        builder.add_edge("generate_batch_summary", END)

        # Compile the graph
        self._graph = builder.compile()
        return self._graph

    def _process_ticket_batch(self, state: TicketTriageState) -> Dict[str, List[Dict]]:
        """
        This is the "MAP" step.
        It takes the list of input tickets and processes them in parallel.
        """
        tickets_in = state["input_tickets"]

        # Create the "worker" chain that classifies one ticket
        # We bind the Pydantic model to the LLM to force structured JSON output
        classify_chain = (
            CLASSIFY_PROMPT_TEMPLATE
            | self.llm.with_structured_output(TicketClassification)
        )

        # Run the "map" in parallel
        # .batch() runs the chain for every item in the `tickets_in` list.
        # We set max_concurrency to 5 for parallel processing.
        classifications = classify_chain.batch(tickets_in, {"max_concurrency": 5})

        # Combine original tickets with new classifications
        processed_tickets = []
        for original, classification in zip(tickets_in, classifications):
            # Add the new 'category' and 'priority' fields to the original ticket dict
            processed_tickets.append({
                **original,
                **classification.model_dump()  # .model_dump() converts Pydantic to dict
            })

        return {"processed_tickets": processed_tickets}

    def _generate_batch_summary(self, state: TicketTriageState) -> Dict[str, str]:
        """
        This is the "REDUCE" step.
        It takes the list of *all* processed tickets and generates a single summary.
        """
        processed_tickets = state["processed_tickets"]

        # Format the ticket data into a single string for the LLM
        tickets_as_string_list = []
        for t in processed_tickets:
            tickets_as_string_list.append(
                f"  - Title: {t['title']}\n"
                f"    Category: {t['category']}\n"
                f"    Priority: {t.get('priority', 'N/A')}\n"
                f"    Description: {t['description']}"
            )
        tickets_as_string = "\n---\n".join(tickets_as_string_list)

        # Create the "reduce" chain with structured output
        llm = self.llm
        summary_chain = (
            SUMMARY_PROMPT_TEMPLATE
            | llm.with_structured_output(BatchSummary)
        )

        # Invoke the chain to get the structured summary
        summary_result = summary_chain.invoke({"tickets_as_string": tickets_as_string})
        summary = summary_result.summary

        return {"batch_summary": summary}

    async def analyze_tickets(
        self, tickets: List[Dict[str, str]]
    ) -> tuple[List[Dict], str]:
        """
        Analyze a batch of tickets using LangGraph.

        Args:
            tickets: List of ticket dictionaries with 'title' and 'description' keys.

        Returns:
            Tuple of (processed_tickets, batch_summary) where:
            - processed_tickets: List of tickets with added 'category' and 'priority' fields
            - batch_summary: Executive summary string of all tickets
        """
        # Build the graph if not already built
        graph = self._build_graph()

        # Prepare input for the graph
        inputs = {"input_tickets": tickets}

        # Run the graph (this is synchronous, but we're in an async context)
        # We'll run it in a thread pool to avoid blocking
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, graph.invoke, inputs)

        return result["processed_tickets"], result["batch_summary"]

