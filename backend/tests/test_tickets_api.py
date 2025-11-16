"""Tests for ticket API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tickets(client: AsyncClient):
    """Test creating tickets via POST /api/tickets."""
    response = await client.post(
        "/api/tickets",
        json=[
            {"title": "New Ticket 1", "description": "Description for ticket 1"},
            {"title": "New Ticket 2", "description": "Description for ticket 2"},
        ],
    )
    
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    
    # Check first ticket
    ticket1 = data[0]
    assert ticket1["title"] == "New Ticket 1"
    assert ticket1["description"] == "Description for ticket 1"
    assert "id" in ticket1
    assert "created_at" in ticket1
    assert ticket1["status"] == "pending"
    
    # Check second ticket
    ticket2 = data[1]
    assert ticket2["title"] == "New Ticket 2"
    assert ticket2["description"] == "Description for ticket 2"
    assert "id" in ticket2
    assert ticket2["id"] != ticket1["id"]


@pytest.mark.asyncio
async def test_create_single_ticket(client: AsyncClient):
    """Test creating a single ticket."""
    response = await client.post(
        "/api/tickets",
        json=[{"title": "Single Ticket", "description": "Single ticket description"}],
    )
    
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Single Ticket"
    assert data[0]["description"] == "Single ticket description"


@pytest.mark.asyncio
async def test_create_tickets_validation_error(client: AsyncClient):
    """Test that validation errors are returned for invalid tickets."""
    # Empty title
    response = await client.post(
        "/api/tickets",
        json=[{"title": "", "description": "Description"}],
    )
    assert response.status_code == 422
    
    # Missing description
    response = await client.post(
        "/api/tickets",
        json=[{"title": "Title"}],
    )
    assert response.status_code == 422
    
    # Missing title
    response = await client.post(
        "/api/tickets",
        json=[{"description": "Description"}],
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_tickets_empty(client: AsyncClient):
    """Test listing tickets when database is empty."""
    response = await client.get("/api/tickets")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["page"] == 1
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_list_tickets_with_data(client: AsyncClient, sample_tickets):
    """Test listing tickets with existing data."""
    response = await client.get("/api/tickets")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2  # Only PENDING tickets
    assert data["page"] == 1
    assert data["page_size"] == 10
    
    # Check that only PENDING tickets are returned
    for ticket in data["items"]:
        assert ticket["status"] == "pending"
        assert ticket["title"].startswith("Test Ticket")


@pytest.mark.asyncio
async def test_list_tickets_pagination(client: AsyncClient):
    """Test ticket pagination."""
    # Create 15 tickets
    tickets_data = [
        {"title": f"Ticket {i}", "description": f"Description {i}"}
        for i in range(15)
    ]
    await client.post("/api/tickets", json=tickets_data)
    
    # First page
    response = await client.get("/api/tickets?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["page"] == 1
    assert data["page_size"] == 10
    
    # Second page
    response = await client.get("/api/tickets?page=2&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["page"] == 2
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_list_tickets_with_status_filter(client: AsyncClient, sample_tickets):
    """Test listing tickets filtered by status."""
    # Filter by pending
    response = await client.get("/api/tickets?status=pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    for ticket in data["items"]:
        assert ticket["status"] == "pending"
    
    # Filter by analyzed
    response = await client.get("/api/tickets?status=analyzed")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "analyzed"


@pytest.mark.asyncio
async def test_list_tickets_invalid_page(client: AsyncClient):
    """Test that invalid page numbers return validation errors."""
    response = await client.get("/api/tickets?page=0")
    assert response.status_code == 422
    
    response = await client.get("/api/tickets?page=-1")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_tickets_invalid_page_size(client: AsyncClient):
    """Test that invalid page sizes return validation errors."""
    response = await client.get("/api/tickets?page_size=0")
    assert response.status_code == 422
    
    response = await client.get("/api/tickets?page_size=1001")  # Max is 1000
    assert response.status_code == 422

