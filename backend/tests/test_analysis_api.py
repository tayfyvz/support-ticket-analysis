"""Tests for analysis API endpoints."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_tickets_all_pending(client: AsyncClient, sample_tickets):
    """Test analyzing all pending tickets."""
    # Mock the background task processing to avoid actual LLM calls
    with patch("app.services.analysis_service.AnalysisService.process_analysis_background") as mock_process:
        mock_process.return_value = None
        
        # Start analysis
        response = await client.post("/api/analyze", json={})
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "created_at" in data
        assert data["summary"] == "Analyzing 2 ticket(s)"
        assert "ticket_analyses" in data
        assert isinstance(data["ticket_analyses"], list)


@pytest.mark.asyncio
async def test_analyze_tickets_specific_ids(client: AsyncClient, sample_tickets):
    """Test analyzing specific ticket IDs."""
    with patch("app.services.analysis_service.AnalysisService.process_analysis_background") as mock_process:
        mock_process.return_value = None
        
        # Analyze specific tickets
        ticket_ids = [sample_tickets[0].id]
        response = await client.post("/api/analyze", json={"ticketIds": ticket_ids})
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["summary"] == "Analyzing 1 ticket(s)"


@pytest.mark.asyncio
async def test_analyze_tickets_no_tickets_available(client: AsyncClient):
    """Test analyzing when no pending tickets are available."""
    response = await client.post("/api/analyze", json={})
    
    assert response.status_code == 400  # Should return error when no tickets to analyze
    assert "No tickets to analyze" in response.json()["detail"]


@pytest.mark.asyncio
async def test_analyze_tickets_invalid_ids(client: AsyncClient, sample_tickets):
    """Test analyzing with invalid ticket IDs."""
    # Try to analyze non-existent tickets
    response = await client.post("/api/analyze", json={"ticketIds": [99999, 99998]})
    
    # Should return error when no tickets found
    assert response.status_code == 400
    assert "No tickets to analyze" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_analysis_runs_empty(client: AsyncClient):
    """Test listing analysis runs when database is empty."""
    response = await client.get("/api/analyze/runs")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_analysis_runs_with_data(client: AsyncClient, sample_analysis_run):
    """Test listing analysis runs with existing data."""
    response = await client.get("/api/analyze/runs")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total"] == 1
    
    # Check analysis run details
    run = data["items"][0]
    assert run["id"] == sample_analysis_run.id
    assert "created_at" in run
    assert run["summary"] == "Test analysis run"
    assert run["ticket_count"] == 2
    assert run["status"] == "completed"  # Both tickets are analyzed


@pytest.mark.asyncio
async def test_list_analysis_runs_pagination(client: AsyncClient, sample_analysis_run):
    """Test analysis runs pagination."""
    # Create another analysis run
    from app.db.session import get_session
    from app.models.entities import AnalysisRun
    from sqlalchemy.ext.asyncio import AsyncSession
    
    # Get the test_db from the fixture (we need to access it differently)
    # For now, let's test with what we have
    response = await client.get("/api/analyze/runs?page=1&page_size=1")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_analysis_runs_invalid_page(client: AsyncClient):
    """Test that invalid page numbers return validation errors."""
    response = await client.get("/api/analyze/runs?page=0")
    assert response.status_code == 422
    
    response = await client.get("/api/analyze/runs?page=-1")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_analysis_runs_invalid_page_size(client: AsyncClient):
    """Test that invalid page sizes return validation errors."""
    response = await client.get("/api/analyze/runs?page_size=0")
    assert response.status_code == 422
    
    response = await client.get("/api/analyze/runs?page_size=101")  # Max is 100
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_analysis_runs_multiple_runs(client: AsyncClient, test_db, sample_tickets):
    """Test listing multiple analysis runs."""
    from app.models.entities import AnalysisRun, TicketStatus
    
    # Create multiple analysis runs
    run1 = AnalysisRun(summary="Run 1")
    run2 = AnalysisRun(summary="Run 2")
    test_db.add_all([run1, run2])
    await test_db.commit()
    await test_db.refresh(run1)
    await test_db.refresh(run2)
    
    response = await client.get("/api/analyze/runs")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2

