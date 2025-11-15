import asyncio
import random
from typing import Sequence

from fastapi import BackgroundTasks
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import AnalysisRun, Ticket, TicketAnalysis, AnalysisStatus
from app.schemas.analysis import AnalysisRunResponse


class AnalysisService:
    """Service layer for ticket analysis operations."""

    # Categories and priorities for random assignment
    CATEGORIES = ["billing", "bug", "feature_request", "support", "technical", "account"]
    PRIORITIES = ["low", "medium", "high"]

    @staticmethod
    async def analyze_tickets(
        db: AsyncSession,
        background_tasks: BackgroundTasks,
        ticket_ids: list[int] | None = None
    ) -> AnalysisRunResponse:
        """Start analysis of tickets - creates analysis run and returns immediately. Processing happens in background."""
        
        # Determine which tickets to analyze
        if ticket_ids:
            # Analyze specific tickets
            result = await db.execute(
                select(Ticket).where(
                    Ticket.id.in_(ticket_ids),
                    ~Ticket.analyses.any()  # Only ready to analyze tickets
                )
            )
            tickets: Sequence[Ticket] = result.scalars().all()
        else:
            # Analyze all ready to analyze tickets
            result = await db.execute(
                select(Ticket).where(~Ticket.analyses.any())
            )
            tickets: Sequence[Ticket] = result.scalars().all()

        if not tickets:
            raise ValueError("No tickets to analyze")

        # Create analysis run with PENDING status
        analysis_run = AnalysisRun(
            summary=f"Analyzing {len(tickets)} ticket(s)",
            status=AnalysisStatus.PENDING.value
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
        """Background task to process ticket analysis with simulated LLM processing time."""
        try:
            # Update status to PROCESSING
            await db.execute(
                update(AnalysisRun)
                .where(AnalysisRun.id == analysis_run_id)
                .values(status=AnalysisStatus.PROCESSING.value)
            )
            await db.commit()

            # Get tickets to analyze
            if ticket_ids:
                result = await db.execute(
                    select(Ticket).where(
                        Ticket.id.in_(ticket_ids),
                        ~Ticket.analyses.any()
                    )
                )
                tickets: Sequence[Ticket] = result.scalars().all()
            else:
                result = await db.execute(
                    select(Ticket).where(~Ticket.analyses.any())
                )
                tickets: Sequence[Ticket] = result.scalars().all()

            # Simulate LLM processing time (2-5 seconds per ticket)
            processing_time = random.uniform(2.0, 5.0) * len(tickets)
            await asyncio.sleep(processing_time)

            # Process each ticket - continue even if one fails
            successful_count = 0
            failed_count = 0

            for ticket in tickets:
                try:
                    category = random.choice(AnalysisService.CATEGORIES)
                    priority = random.choice(AnalysisService.PRIORITIES)
                    notes = f"Auto-analyzed: {category} issue with {priority} priority"

                    ticket_analysis = TicketAnalysis(
                        analysis_run_id=analysis_run_id,
                        ticket_id=ticket.id,
                        category=category,
                        priority=priority,
                        notes=notes,
                    )
                    db.add(ticket_analysis)
                    successful_count += 1
                except Exception as e:
                    # Log error but continue with other tickets
                    failed_count += 1
                    print(f"Error analyzing ticket {ticket.id}: {e}")

            # Update summary and status
            summary = f"Analyzed {successful_count} ticket(s)"
            if failed_count > 0:
                summary += f", {failed_count} failed"

            await db.execute(
                update(AnalysisRun)
                .where(AnalysisRun.id == analysis_run_id)
                .values(
                    status=AnalysisStatus.COMPLETED.value,
                    summary=summary
                )
            )
            await db.commit()

        except Exception as e:
            # Mark as failed on error
            await db.execute(
                update(AnalysisRun)
                .where(AnalysisRun.id == analysis_run_id)
                .values(
                    status=AnalysisStatus.FAILED.value,
                    summary=f"Analysis failed: {str(e)}"
                )
            )
            await db.commit()
            raise

