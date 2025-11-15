from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analyses: Mapped[List["TicketAnalysis"]] = relationship(back_populates="ticket")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    ticket_analyses: Mapped[List["TicketAnalysis"]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")


class TicketAnalysis(Base):
    __tablename__ = "ticket_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"))
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(String(100))
    priority: Mapped[str] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    analysis_run: Mapped["AnalysisRun"] = relationship(back_populates="ticket_analyses")
    ticket: Mapped["Ticket"] = relationship(back_populates="analyses")

