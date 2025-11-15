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
    """Get the current status of an analysis run."""
    from sqlalchemy.orm import joinedload
    
    result = await db.execute(
        select(AnalysisRun)
        .where(AnalysisRun.id == analysis_run_id)
        .options(joinedload(AnalysisRun.ticket_analyses))
    )
    analysis_run = result.unique().scalar_one_or_none()
    
    if not analysis_run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    
    # Get ticket IDs from ticket_analyses if they exist
    # If analysis is still pending/processing, ticket_analyses might be empty
    ticket_ids = [ta.ticket_id for ta in analysis_run.ticket_analyses] if analysis_run.ticket_analyses else []
    
    return AnalysisStatusResponse(
        analysis_run_id=analysis_run.id,
        status=analysis_run.status,  # status is already a string
        ticket_ids=ticket_ids
    )

