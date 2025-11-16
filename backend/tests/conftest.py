"""Pytest configuration and fixtures for testing."""

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from app.db.session import Base, get_session
from app.main import create_app
from app.models.entities import Ticket, AnalysisRun, TicketAnalysis, TicketStatus


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with in-memory SQLite."""
    # Create engine with in-memory SQLite
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Create session
    async with async_session_maker() as session:
        yield session
        await session.rollback()
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with dependency overrides."""
    app = create_app()
    
    # Override the database dependency
    async def override_get_session():
        yield test_db
    
    app.dependency_overrides[get_session] = override_get_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_tickets(test_db: AsyncSession) -> list[Ticket]:
    """Create sample tickets for testing."""
    tickets = [
        Ticket(title="Test Ticket 1", description="Description 1", status=TicketStatus.PENDING.value),
        Ticket(title="Test Ticket 2", description="Description 2", status=TicketStatus.PENDING.value),
        Ticket(title="Test Ticket 3", description="Description 3", status=TicketStatus.ANALYZED.value),
    ]
    test_db.add_all(tickets)
    await test_db.commit()
    for ticket in tickets:
        await test_db.refresh(ticket)
    return tickets


@pytest_asyncio.fixture
async def sample_analysis_run(test_db: AsyncSession, sample_tickets: list[Ticket]) -> AnalysisRun:
    """Create a sample analysis run with ticket analyses."""
    analysis_run = AnalysisRun(summary="Test analysis run")
    test_db.add(analysis_run)
    await test_db.flush()
    
    # Create ticket analyses for the first two tickets
    ticket_analyses = [
        TicketAnalysis(
            analysis_run_id=analysis_run.id,
            ticket_id=sample_tickets[0].id,
            category="bug",
            priority="high",
            notes="Test notes 1",
        ),
        TicketAnalysis(
            analysis_run_id=analysis_run.id,
            ticket_id=sample_tickets[1].id,
            category="feature_request",
            priority="medium",
            notes="Test notes 2",
        ),
    ]
    test_db.add_all(ticket_analyses)
    
    # Update ticket statuses
    sample_tickets[0].status = TicketStatus.ANALYZED.value
    sample_tickets[1].status = TicketStatus.ANALYZED.value
    
    await test_db.commit()
    await test_db.refresh(analysis_run)
    return analysis_run

