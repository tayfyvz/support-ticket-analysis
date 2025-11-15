from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.ticket import (
    AnalyzedTicketListResponse,
    TicketCreateRequest,
    TicketListResponse,
    TicketResponse,
)
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", response_model=list[TicketResponse], status_code=201)
async def create_tickets(
    tickets: list[TicketCreateRequest],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[TicketResponse]:
    """Create one or more tickets."""
    return await TicketService.create_tickets(db, tickets)


@router.get("/analyzed", response_model=AnalyzedTicketListResponse)
async def list_analyzed_tickets(
    db: Annotated[AsyncSession, Depends(get_session)],
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
) -> AnalyzedTicketListResponse:
    """List analyzed tickets with pagination."""
    return await TicketService.list_analyzed_tickets(db, page=page, page_size=page_size)


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    db: Annotated[AsyncSession, Depends(get_session)],
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
) -> TicketListResponse:
    """List tickets with pagination."""
    return await TicketService.list_tickets(db, page=page, page_size=page_size)
