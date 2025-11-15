from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.entities import Ticket, TicketAnalysis
from app.schemas.ticket import (
    AnalyzedTicketListResponse,
    AnalyzedTicketResponse,
    TicketCreateRequest,
    TicketListResponse,
    TicketResponse,
)


class TicketService:
    """Service layer for ticket operations."""

    @staticmethod
    async def create_tickets(
        db: AsyncSession, ticket_requests: list[TicketCreateRequest]
    ) -> list[TicketResponse]:
        """Create one or more tickets in the database."""
        db_tickets = [
            Ticket(title=ticket.title, description=ticket.description)
            for ticket in ticket_requests
        ]
        db.add_all(db_tickets)
        await db.commit()
        
        # Refresh to get generated IDs and timestamps
        for db_ticket in db_tickets:
            await db.refresh(db_ticket)
        
        return [TicketResponse.model_validate(t) for t in db_tickets]

    @staticmethod
    async def list_tickets(
        db: AsyncSession, page: int = 1, page_size: int = 10
    ) -> TicketListResponse:
        """List tickets with pagination, limited to tickets without analyses."""
        offset = (page - 1) * page_size


        # Get paginated tickets
        result = await db.execute(
            select(Ticket).where(~Ticket.analyses.any())
            .order_by(Ticket.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        tickets: Sequence[Ticket] = result.scalars().all()

        return TicketListResponse(
            items=[TicketResponse.model_validate(t) for t in tickets],
            page=page,
            page_size=page_size,
        )

    @staticmethod
    async def list_analyzed_tickets(
        db: AsyncSession, page: int = 1, page_size: int = 10
    ) -> AnalyzedTicketListResponse:
        """List analyzed tickets with pagination, including analysis details."""
        offset = (page - 1) * page_size

        # Get paginated ticket analyses with their tickets
        result = await db.execute(
            select(TicketAnalysis)
            .join(Ticket)
            .options(joinedload(TicketAnalysis.ticket))
            .order_by(TicketAnalysis.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        ticket_analyses: Sequence[TicketAnalysis] = result.unique().scalars().all()

        # Convert to AnalyzedTicketResponse format
        analyzed_tickets = []
        for analysis in ticket_analyses:
            analyzed_tickets.append(
                AnalyzedTicketResponse(
                    id=analysis.ticket.id,
                    title=analysis.ticket.title,
                    description=analysis.ticket.description,
                    priority=analysis.priority,
                    category=analysis.category,
                    notes=analysis.notes,
                )
            )

        return AnalyzedTicketListResponse(
            items=analyzed_tickets,
            page=page,
            page_size=page_size,
        )

