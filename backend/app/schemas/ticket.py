from datetime import datetime

from pydantic import BaseModel, Field


class TicketCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    page: int
    page_size: int


class AnalyzedTicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    category: str
    notes: str | None

    class Config:
        from_attributes = True


class AnalyzedTicketListResponse(BaseModel):
    items: list[AnalyzedTicketResponse]
    page: int
    page_size: int
