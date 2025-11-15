from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.schemas.analysis import AnalyzeRequest, AnalysisRunResponse, AnalysisStatusResponse
from app.services.analysis_service import AnalysisService
from app.models.entities import AnalysisRun

router = APIRouter(prefix="/api/analyze", tags=["analysis"])


@router.post("", response_model=AnalysisRunResponse, status_code=201)
async def analyze_tickets(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AnalysisRunResponse:
    """Start analysis of tickets. If ticketIds provided, analyze only those; otherwise analyze all ready to analyze tickets.
    Returns immediately with analysis_run_id. Processing happens in background."""
    return await AnalysisService.analyze_tickets(db, background_tasks, request.ticketIds)


@router.get("/{analysis_run_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    analysis_run_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AnalysisStatusResponse:
    """Get the current status of an analysis run by checking ticket statuses."""
    from sqlalchemy.orm import joinedload
    from app.models.entities import Ticket, TicketStatus
    
    result = await db.execute(
        select(AnalysisRun)
        .where(AnalysisRun.id == analysis_run_id)
        .options(joinedload(AnalysisRun.ticket_analyses))
    )
    analysis_run = result.unique().scalar_one_or_none()
    
    if not analysis_run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    
    # Get ticket IDs from ticket_analyses if they exist
    ticket_ids = [ta.ticket_id for ta in analysis_run.ticket_analyses] if analysis_run.ticket_analyses else []
    
    # If no ticket_analyses yet, try to find tickets with PROCESSING status
    # that might belong to this run (we can't be 100% sure, but it's a best guess)
    if not ticket_ids:
        # This is a limitation - we don't store which tickets belong to which run
        # But we can check for PROCESSING tickets
        tickets_result = await db.execute(
            select(Ticket).where(Ticket.status == TicketStatus.PROCESSING.value)
        )
        processing_tickets = tickets_result.scalars().all()
        ticket_ids = [t.id for t in processing_tickets]
    
    # Determine overall status based on ticket statuses
    if ticket_ids:
        tickets_result = await db.execute(
            select(Ticket).where(Ticket.id.in_(ticket_ids))
        )
        tickets = tickets_result.scalars().all()
        
        # Check if all tickets are analyzed
        if all(t.status == TicketStatus.ANALYZED.value for t in tickets):
            status = "completed"
        # Check if any tickets failed
        elif any(t.status == TicketStatus.FAILED.value for t in tickets):
            status = "failed"
        # Check if any tickets are still processing
        elif any(t.status == TicketStatus.PROCESSING.value for t in tickets):
            status = "processing"
        else:
            status = "pending"
    else:
        status = "pending"
    
    return AnalysisStatusResponse(
        analysis_run_id=analysis_run.id,
        status=status,
        ticket_ids=ticket_ids
    )


@router.get("/active", response_model=list[AnalysisStatusResponse])
async def get_active_analysis_runs(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[AnalysisStatusResponse]:
    """Get all active analysis runs (with processing or pending tickets)."""
    from sqlalchemy.orm import joinedload
    from app.models.entities import Ticket, TicketStatus
    
    # Get all analysis runs that might be active
    # We'll check recent runs (last hour) or runs with processing tickets
    from datetime import datetime, timedelta
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    result = await db.execute(
        select(AnalysisRun)
        .where(AnalysisRun.created_at >= one_hour_ago)
        .options(joinedload(AnalysisRun.ticket_analyses))
        .order_by(AnalysisRun.created_at.desc())
    )
    recent_runs = result.unique().scalars().all()
    
    active_runs = []
    for run in recent_runs:
        # Get ticket IDs from ticket_analyses if they exist
        ticket_ids = [ta.ticket_id for ta in run.ticket_analyses] if run.ticket_analyses else []
        
        # If no ticket_analyses yet, check if there are processing tickets
        # that might belong to this run
        if not ticket_ids:
            # Check for processing tickets created around the same time as the run
            tickets_result = await db.execute(
                select(Ticket).where(
                    Ticket.status == TicketStatus.PROCESSING.value,
                    Ticket.created_at <= run.created_at + timedelta(minutes=5)
                )
            )
            processing_tickets = tickets_result.scalars().all()
            if processing_tickets:
                ticket_ids = [t.id for t in processing_tickets]
        
        # Check if any of these tickets are still processing
        if ticket_ids:
            tickets_result = await db.execute(
                select(Ticket).where(Ticket.id.in_(ticket_ids))
            )
            tickets = tickets_result.scalars().all()
            
            # Only include runs that have processing tickets
            if any(t.status == TicketStatus.PROCESSING.value for t in tickets):
                # Determine status
                if all(t.status == TicketStatus.ANALYZED.value for t in tickets):
                    status = "completed"
                elif any(t.status == TicketStatus.FAILED.value for t in tickets):
                    status = "failed"
                elif any(t.status == TicketStatus.PROCESSING.value for t in tickets):
                    status = "processing"
                else:
                    status = "pending"
                
                active_runs.append(AnalysisStatusResponse(
                    analysis_run_id=run.id,
                    status=status,
                    ticket_ids=ticket_ids
                ))
    
    return active_runs

