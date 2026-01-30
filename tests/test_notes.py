def test_create_note(client, auth_headers):
    """Test creating a note."""
    response = client.post(
        "/api/v1/notes/",
        json={"title": "Test Note", "content": "Test content", "tags": ["test"]},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test content"
    assert data["tags"] == ["test"]
    assert "id" in data


def test_create_note_without_auth(client):
    """Test creating note without authentication fails."""
    response = client.post(
        "/api/v1/notes/",
        json={"title": "Test", "content": "Content"}
    )
    assert response.status_code == 403


def test_list_notes(client, auth_headers):
    """Test listing notes."""
    # Create two notes
    client.post(
        "/api/v1/notes/",
        json={"title": "Note 1", "content": "Content 1"},
        headers=auth_headers
    )
    client.post(
        "/api/v1/notes/",
        json={"title": "Note 2", "content": "Content 2"},
        headers=auth_headers
    )
    
    # List notes
    response = client.get("/api/v1/notes/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_note(client, auth_headers):
    """Test getting a specific note."""
    # Create note
    create_response = client.post(
        "/api/v1/notes/",
        json={"title": "Test", "content": "Content"},
        headers=auth_headers
    )
    note_id = create_response.json()["id"]
    
    # Get note
    response = client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == note_id


def test_update_note(client, auth_headers):
    """Test updating a note."""
    # Create note
    create_response = client.post(
        "/api/v1/notes/",
        json={"title": "Original", "content": "Original content"},
        headers=auth_headers
    )
    note_id = create_response.json()["id"]
    
    # Update note
    response = client.put(
        f"/api/v1/notes/{note_id}",
        json={"title": "Updated"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["content"] == "Original content"  # Unchanged


def test_delete_note(client, auth_headers):
    """Test deleting a note."""
    # Create note
    create_response = client.post(
        "/api/v1/notes/",
        json={"title": "To Delete", "content": "Content"},
        headers=auth_headers
    )
    note_id = create_response.json()["id"]
    
    # Delete note
    response = client.delete(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify deleted
    get_response = client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert get_response.status_code == 404