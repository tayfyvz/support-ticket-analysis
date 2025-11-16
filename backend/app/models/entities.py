from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
import sqlalchemy as sa

from app.db.session import Base


class TicketStatus(str, enum.Enum):
    """Status of a ticket."""
    PENDING = "pending"  # Ready to analyze
    PROCESSING = "processing"  # Currently being analyzed
    ANALYZED = "analyzed"  # Analysis completed
    FAILED = "failed"  # Analysis failed


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(
        SQLEnum(TicketStatus, name="ticket_status", native_enum=True, create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        default=TicketStatus.PENDING.value,
        server_default=sa.text("'pending'")
    )

    analyses: Mapped[List["TicketAnalysis"]] = relationship(back_populates="ticket")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    ticket_analyses: Mapped[List["TicketAnalysis"]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")


class TicketCategory(str, enum.Enum):
    """Category of ticket analysis."""
    BILLING = "billing"
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    SUPPORT = "support"
    TECHNICAL = "technical"
    ACCOUNT = "account"


class TicketAnalysis(Base):
    __tablename__ = "ticket_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"))
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(
        SQLEnum(
            TicketCategory,
            name="ticket_category",
            native_enum=True,
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    priority: Mapped[str] = mapped_column(
        SQLEnum(
            "low",
            "medium",
            "high",
            name="ticket_priority",
            native_enum=True,
            create_constraint=True,
        ),
        nullable=False,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    analysis_run: Mapped["AnalysisRun"] = relationship(back_populates="ticket_analyses")
    ticket: Mapped["Ticket"] = relationship(back_populates="analyses")

