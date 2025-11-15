from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entities import Ticket
from app.schemas.ticket import TicketCreate, TicketListResponse, TicketResponse

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", response_model=list[TicketResponse], status_code=201)
async def create_tickets(
    tickets: list[TicketCreate],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[TicketResponse]:
    """Create one or more tickets."""
    db_tickets = [
        Ticket(title=ticket.title, description=ticket.description)
        for ticket in tickets
    ]
    db.add_all(db_tickets)
    await db.commit()
    for db_ticket in db_tickets:
        await db.refresh(db_ticket)
    return [TicketResponse.model_validate(t) for t in db_tickets]


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> TicketListResponse:
    """List tickets with pagination."""
    offset = (page - 1) * page_size

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(Ticket))
    total = count_result.scalar_one()

    # Get paginated tickets
    result = await db.execute(
        select(Ticket)
        .order_by(Ticket.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    tickets = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return TicketListResponse(
        items=[TicketResponse.model_validate(t) for t in tickets],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

