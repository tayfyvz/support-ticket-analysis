from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Ticket
from app.schemas.ticket import TicketCreateRequest, TicketListResponse, TicketResponse


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

