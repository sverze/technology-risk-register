# Integration Tests

This directory contains integration tests for the Technology Risk Register API. These tests run against a live API instance to verify end-to-end functionality.

## Running the Tests

### Prerequisites

1. **Install test dependencies:**
   ```bash
   uv sync --group test
   ```

2. **Start the API server** (choose one):

   **Local Development Server:**
   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

   **Docker Container:**
   ```bash
   docker-compose up
   ```

### Test Execution Options

#### Option 1: Using the Test Runner Script (Recommended)

```bash
# Test against local server (default)
python run_integration_tests.py

# Test against custom URL
python run_integration_tests.py --url http://localhost:8001

# Skip health check (if API is already verified)
python run_integration_tests.py --no-health-check

# Increase wait timeout for slower startup
python run_integration_tests.py --wait-timeout 60
```

#### Option 2: Direct pytest execution

```bash
# Test against default local server
API_BASE_URL=http://localhost:8000 uv run pytest tests/integration/ -v

# Test against Docker container
API_BASE_URL=http://localhost:8000 uv run pytest tests/integration/ -v

# Test against custom URL
API_BASE_URL=http://your-server:port uv run pytest tests/integration/ -v
```

#### Option 3: Run specific test classes

```bash
# Test only dropdown endpoints
uv run pytest tests/integration/test_integration.py::TestDropdownEndpoints -v

# Test only risk management
uv run pytest tests/integration/test_integration.py::TestRiskEndpoints -v

# Test only dashboard
uv run pytest tests/integration/test_integration.py::TestDashboardEndpoints -v
```

## Test Coverage

The integration tests cover:

### 🏥 **Health & Basics**
- Health endpoint (`/health`)
- Root endpoint (`/`)
- OpenAPI documentation accessibility

### 📋 **Dropdown Endpoints**
- Get all categories
- Get all dropdown values
- Filter by category
- Group by category

### 📊 **Dashboard Endpoints**
- Complete dashboard data retrieval
- Data structure validation
- All dashboard components

### 🎯 **Risk Management Endpoints**
- **List Operations:**
  - Paginated risk retrieval
  - Search functionality
  - Category filtering
  - Sorting options
  - Pagination limits validation

- **Individual Operations:**
  - Get specific risk
  - Create new risk
  - Update existing risk
  - Delete risk
  - Error handling for non-existent risks

### 📝 **Risk Update Endpoints**
- Get updates for specific risk
- Get recent updates across all risks
- Limit validation
- Error handling

### ⚠️ **Error Handling**
- Invalid endpoints (404)
- Invalid HTTP methods (405)
- Malformed JSON (422)
- Missing required fields (422)

## Test Data

The integration tests:
- **Use existing sample data** seeded by the application
- **Create temporary test data** for CRUD operations
- **Clean up after themselves** (delete created test risks)
- **Don't interfere** with existing data

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `http://localhost:8000` | Base URL of the API to test |

## Troubleshooting

### API Not Responding
```
❌ API at http://localhost:8000 is not responding or unhealthy
```

**Solutions:**
1. Make sure the API server is running
2. Check the URL is correct
3. Verify the port is accessible
4. Check firewall settings

### Connection Refused
```
requests.exceptions.ConnectionError: Connection refused
```

**Solutions:**
1. Ensure the API server is started
2. Verify the port (8000 by default)
3. Check if another process is using the port

### Tests Fail with 404 Errors
This usually means:
1. The API server isn't running
2. The base URL is incorrect
3. The API routes have changed

### Sample Data Missing
If tests fail because no sample data exists:
1. Restart the API server to trigger data seeding
2. Check database connectivity
3. Verify `seed_sample_risks()` is being called

## Adding New Tests

To add new integration tests:

1. **Add test methods** to existing classes or create new test classes
2. **Follow the naming convention**: `test_*`
3. **Use appropriate assertions** for HTTP status codes and response structure
4. **Clean up** any test data you create
5. **Handle edge cases** appropriately

Example:
```python
def test_new_endpoint(self):
    """Test a new API endpoint."""
    response = requests.get(f"{API_V1_BASE}/new-endpoint")
    assert response.status_code == 200
    
    data = response.json()
    assert "expected_field" in data
```