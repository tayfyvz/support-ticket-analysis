from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.ticket import TicketResponse


class AnalyzeRequest(BaseModel):
    ticketIds: Optional[list[int]] = None


class TicketAnalysisResponse(BaseModel):
    id: int
    ticket_id: int
    category: str
    priority: str
    notes: Optional[str] = None
    ticket: Optional[TicketResponse] = None

    class Config:
        from_attributes = True


class AnalysisRunResponse(BaseModel):
    id: int
    created_at: datetime
    summary: Optional[str] = None
    status: str
    ticket_analyses: list[TicketAnalysisResponse] = []

    class Config:
        from_attributes = True


class AnalysisStatusResponse(BaseModel):
    analysis_run_id: int
    status: str  # "pending", "processing", "completed", "failed"
    ticket_ids: list[int] = []

