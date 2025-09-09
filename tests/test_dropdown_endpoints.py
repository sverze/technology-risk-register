def test_get_dropdown_values_no_filter(client, sample_dropdown_values):
    """Test GET /dropdown/values without category filter."""
    response = client.get("/api/v1/dropdown/values")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify structure
    for item in data:
        assert "id" in item
        assert "category" in item
        assert "value" in item
        assert "display_order" in item
        assert "is_active" in item
        assert item["is_active"] is True


def test_get_dropdown_values_with_category_filter(client, sample_dropdown_values):
    """Test GET /dropdown/values with category filter."""
    response = client.get("/api/v1/dropdown/values?category=risk_status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    
    for item in data:
        assert item["category"] == "risk_status"
        assert item["is_active"] is True


def test_get_dropdown_values_nonexistent_category(client, sample_dropdown_values):
    """Test GET /dropdown/values with nonexistent category."""
    response = client.get("/api/v1/dropdown/values?category=nonexistent")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_dropdown_categories(client, sample_dropdown_values):
    """Test GET /dropdown/categories."""
    response = client.get("/api/v1/dropdown/categories")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Should include our test categories
    expected_categories = ["risk_category", "risk_status", "risk_response_strategy", "control_status", "business_criticality"]
    for expected_category in expected_categories:
        assert expected_category in data
    
    # Should be sorted alphabetically
    assert data == sorted(data)


def test_get_dropdown_values_by_category_all(client, sample_dropdown_values):
    """Test GET /dropdown/values/by-category without specific categories."""
    response = client.get("/api/v1/dropdown/values/by-category")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Check structure
    for category, values in data.items():
        assert isinstance(category, str)
        assert isinstance(values, list)
        assert len(values) > 0
        
        for value in values:
            assert value["category"] == category
            assert value["is_active"] is True


def test_get_dropdown_values_by_category_specific(client, sample_dropdown_values):
    """Test GET /dropdown/values/by-category with specific categories."""
    response = client.get("/api/v1/dropdown/values/by-category?categories=risk_status&categories=risk_category")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, dict)
    
    # Should only include requested categories
    for category in data.keys():
        assert category in ["risk_status", "risk_category"]
    
    # Verify each category has values
    for category, values in data.items():
        assert len(values) > 0
        for value in values:
            assert value["category"] == category
            assert value["is_active"] is True


def test_get_dropdown_values_by_category_nonexistent(client, sample_dropdown_values):
    """Test GET /dropdown/values/by-category with nonexistent categories."""
    response = client.get("/api/v1/dropdown/values/by-category?categories=nonexistent")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, dict)
    assert len(data) == 0