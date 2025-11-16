from typing import Sequence

from fastapi import BackgroundTasks
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import AnalysisRun, Ticket, TicketAnalysis, TicketStatus
from app.schemas.analysis import AnalysisRunResponse
from app.services.llm_service import LLMService


class AnalysisService:
    """Service layer for ticket analysis operations."""

    @staticmethod
    async def list_analysis_runs(
        db: AsyncSession, page: int = 1, page_size: int = 10
    ) -> dict:
        """List all analysis runs with pagination."""
        from app.schemas.analysis import AnalysisRunListItem
        from sqlalchemy import func
        from app.models.entities import Ticket, TicketStatus
        
        offset = (page - 1) * page_size

        # Get total count
        total_result = await db.execute(select(func.count(AnalysisRun.id)))
        total = total_result.scalar_one()

        # Get paginated analysis runs with ticket_analyses loaded
        from sqlalchemy.orm import joinedload
        
        result = await db.execute(
            select(AnalysisRun)
            .options(joinedload(AnalysisRun.ticket_analyses))
            .order_by(AnalysisRun.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        runs = result.unique().scalars().all()

        # Build response with status and ticket count
        items = []
        for run in runs:
            # Get ticket count from ticket_analyses
            ticket_count = len(run.ticket_analyses) if run.ticket_analyses else 0
            
            # Determine status based on ticket statuses
            if ticket_count > 0:
                ticket_ids = [ta.ticket_id for ta in run.ticket_analyses]
                tickets_result = await db.execute(
                    select(Ticket).where(Ticket.id.in_(ticket_ids))
                )
                tickets = tickets_result.scalars().all()
                
                if all(t.status == TicketStatus.ANALYZED.value for t in tickets):
                    status = "completed"
                elif any(t.status == TicketStatus.FAILED.value for t in tickets):
                    status = "failed"
                elif any(t.status == TicketStatus.PROCESSING.value for t in tickets):
                    status = "processing"
                else:
                    status = "pending"
            else:
                # No tickets yet, check if there are processing tickets that might belong
                tickets_result = await db.execute(
                    select(Ticket).where(Ticket.status == TicketStatus.PROCESSING.value)
                )
                processing_tickets = tickets_result.scalars().all()
                if processing_tickets:
                    status = "processing"
                    ticket_count = len(processing_tickets)
                else:
                    status = "pending"
            
            items.append(AnalysisRunListItem(
                id=run.id,
                created_at=run.created_at,
                summary=run.summary,
                ticket_count=ticket_count,
                status=status
            ))

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total
        }

    @staticmethod
    async def get_analysis_run_details(
        db: AsyncSession, analysis_run_id: int
    ) -> AnalysisRunResponse:
        """Get detailed information about a specific analysis run."""
        from sqlalchemy.orm import joinedload
        
        result = await db.execute(
            select(AnalysisRun)
            .where(AnalysisRun.id == analysis_run_id)
            .options(
                joinedload(AnalysisRun.ticket_analyses).joinedload(TicketAnalysis.ticket)
            )
        )
        analysis_run = result.unique().scalar_one_or_none()
        
        if not analysis_run:
            raise ValueError(f"Analysis run {analysis_run_id} not found")
        
        return AnalysisRunResponse.model_validate(analysis_run)

    @staticmethod
    async def analyze_tickets(
        db: AsyncSession,
        background_tasks: BackgroundTasks,
        ticket_ids: list[int] | None = None
    ) -> AnalysisRunResponse:
        """Start analysis of tickets - creates analysis run and returns immediately. Processing happens in background."""
        
        # Determine which tickets to analyze
        if ticket_ids:
            # Analyze specific tickets with PENDING status
            result = await db.execute(
                select(Ticket).where(
                    Ticket.id.in_(ticket_ids),
                    Ticket.status == TicketStatus.PENDING.value
                )
            )
            tickets: Sequence[Ticket] = result.scalars().all()
        else:
            # Analyze all ready to analyze tickets (PENDING status)
            result = await db.execute(
                select(Ticket).where(Ticket.status == TicketStatus.PENDING.value)
            )
            tickets: Sequence[Ticket] = result.scalars().all()

        if not tickets:
            raise ValueError("No tickets to analyze")

        # Update ticket statuses to PROCESSING
        for ticket in tickets:
            ticket.status = TicketStatus.PROCESSING.value
        await db.flush()

        # Create analysis run
        analysis_run = AnalysisRun(
            summary=f"Analyzing {len(tickets)} ticket(s)"
        )
        db.add(analysis_run)
        await db.flush()  # Get the ID
        await db.commit()

        # Start background processing with a new session
        from app.db.session import async_session_factory
        
        async def process_with_new_session():
            async with async_session_factory() as new_db:
                await AnalysisService.process_analysis_background(
                    new_db,
                    analysis_run.id,
                    ticket_ids
                )
        
        background_tasks.add_task(process_with_new_session)

        # Return immediately with the analysis run
        from sqlalchemy.orm import joinedload
        
        result = await db.execute(
            select(AnalysisRun)
            .where(AnalysisRun.id == analysis_run.id)
            .options(
                joinedload(AnalysisRun.ticket_analyses).joinedload(TicketAnalysis.ticket)
            )
        )
        analysis_run = result.unique().scalar_one()

        return AnalysisRunResponse.model_validate(analysis_run)

    @staticmethod
    async def process_analysis_background(
        db: AsyncSession, analysis_run_id: int, ticket_ids: list[int] | None = None
    ) -> None:
        """Background task to process ticket analysis using LLM."""
        try:

            # Get tickets to analyze (should be PROCESSING status)
            if ticket_ids:
                result = await db.execute(
                    select(Ticket).where(
                        Ticket.id.in_(ticket_ids),
                        Ticket.status == TicketStatus.PROCESSING.value
                    )
                )
                tickets: Sequence[Ticket] = result.scalars().all()
            else:
                result = await db.execute(
                    select(Ticket).where(Ticket.status == TicketStatus.PROCESSING.value)
                )
                tickets: Sequence[Ticket] = result.scalars().all()

            if not tickets:
                return

            # Prepare tickets for LLM processing
            tickets_for_llm = [
                {
                    "title": ticket.title,
                    "description": ticket.description
                }
                for ticket in tickets
            ]

            # Initialize LLM service and analyze tickets
            llm_service = LLMService()
            processed_tickets, batch_summary = await llm_service.analyze_tickets(tickets_for_llm)

            # Process each ticket - continue even if one fails
            successful_count = 0
            failed_count = 0

            # Create a mapping of title+description to processed ticket for lookup
            processed_map = {
                (pt["title"], pt["description"]): pt
                for pt in processed_tickets
            }

            for ticket in tickets:
                try:
                    # Find the corresponding processed ticket
                    processed = processed_map.get((ticket.title, ticket.description))
                    if not processed:
                        raise ValueError(f"Processed ticket not found for ticket {ticket.id}: {ticket.title}")
                    
                    category = processed["category"]
                    priority = processed["priority"]
                    # Use LLM-generated notes if available, otherwise empty string
                    notes = processed.get("notes") or None

                    ticket_analysis = TicketAnalysis(
                        analysis_run_id=analysis_run_id,
                        ticket_id=ticket.id,
                        category=category,
                        priority=priority,
                        notes=notes,
                    )
                    db.add(ticket_analysis)
                    # Update ticket status to ANALYZED
                    ticket.status = TicketStatus.ANALYZED.value
                    successful_count += 1
                except Exception as e:
                    # Log error but continue with other tickets
                    # Update ticket status to FAILED
                    ticket.status = TicketStatus.FAILED.value
                    failed_count += 1
                    print(f"Error analyzing ticket {ticket.id}: {e}")

            # Update summary with LLM-generated summary or fallback
            if successful_count > 0:
                summary = batch_summary if batch_summary else f"Analyzed {successful_count} ticket(s)"
            else:
                summary = "Analysis completed with no successful results"
            
            if failed_count > 0:
                summary += f", {failed_count} failed"

            await db.execute(
                update(AnalysisRun)
                .where(AnalysisRun.id == analysis_run_id)
                .values(summary=summary)
            )
            await db.commit()

        except Exception as e:
            # Mark tickets as failed on error
            if ticket_ids:
                await db.execute(
                    update(Ticket)
                    .where(Ticket.id.in_(ticket_ids))
                    .values(status=TicketStatus.FAILED.value)
                )
            else:
                # Mark all tickets without analyses as failed
                await db.execute(
                    update(Ticket)
                    .where(~Ticket.analyses.any())
                    .values(status=TicketStatus.FAILED.value)
                )
            
            await db.execute(
                update(AnalysisRun)
                .where(AnalysisRun.id == analysis_run_id)
                .values(summary=f"Analysis failed: {str(e)}")
            )
            await db.commit()
            raise

