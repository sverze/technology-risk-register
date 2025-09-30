---
description: Test the Risk Register API endpoints with a complete workflow
argument-hint: "[--public] [--base-url URL]"
allowed-tools:
  - Bash
---

# Test Risk Register API

Test the Risk Register API endpoints with a complete workflow:
1. Create a test risk
2. Update the risk
3. Create a risk log entry
4. Delete the risk

## Usage Options
- `--public`: Test the deployed API instead of local
- `--base-url URL`: Test a custom API endpoint
- Default: Tests local API at http://localhost:8080

I'll run a comprehensive API test workflow using your arguments: `$ARGUMENTS`

Let me parse the arguments and execute the test workflow:

```bash
#!/bin/bash

# Parse arguments for API testing
ARGS="$ARGUMENTS"
BASE_URL="http://localhost:8080/api/v1"
ENV_TYPE="local"

# Parse command line arguments
if echo "$ARGS" | grep -q -- "--public"; then
    BASE_URL="https://your-deployed-app.run.app/api/v1"
    ENV_TYPE="public"
fi

if echo "$ARGS" | grep -q -- "--base-url"; then
    CUSTOM_URL=$(echo "$ARGS" | sed -n 's/.*--base-url \([^ ]*\).*/\1/p')
    if [ -n "$CUSTOM_URL" ]; then
        BASE_URL="$CUSTOM_URL"
        ENV_TYPE="custom"
    fi
fi

echo "🧪 Testing Risk Register API ($ENV_TYPE environment)"
echo "📍 Base URL: $BASE_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to make HTTP requests with error handling
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4

    echo -e "${BLUE}➤ $description${NC}"
    echo "  $method $BASE_URL$endpoint"

    if [ -n "$data" ]; then
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint" 2>/dev/null || echo "HTTP_STATUS:000")
    else
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X "$method" \
            "$BASE_URL$endpoint" 2>/dev/null || echo "HTTP_STATUS:000")
    fi

    # Extract status code and body
    status_code=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS:/d')

    if [[ "$status_code" -ge 200 && "$status_code" -lt 300 ]]; then
        echo -e "  ${GREEN}✓ Success ($status_code)${NC}"
        if command -v jq &> /dev/null; then
            echo "$body" | jq '.' 2>/dev/null || echo "$body"
        else
            echo "$body"
        fi
        echo ""
        return 0
    else
        echo -e "  ${RED}✗ Failed ($status_code)${NC}"
        if command -v jq &> /dev/null; then
            echo "$body" | jq '.' 2>/dev/null || echo "$body"
        else
            echo "$body"
        fi
        echo ""
        return 1
    fi
}

# Test variables
RISK_ID=""
LOG_ENTRY_ID=""

echo "🚀 Starting API test workflow..."
echo ""

# Step 1: Create a risk
echo -e "${YELLOW}Step 1: Creating a test risk${NC}"
CREATE_RISK_DATA='{
  "risk_title": "API Test Risk",
  "risk_category": "Technology",
  "risk_description": "This is a test risk created by the /test-api command",
  "risk_status": "Active",
  "risk_response_strategy": "Mitigate",
  "planned_mitigations": "Implement monitoring and testing",
  "preventative_controls_coverage": "Adequate",
  "preventative_controls_effectiveness": "Effective",
  "preventative_controls_description": "Automated testing and code reviews",
  "detective_controls_coverage": "Adequate",
  "detective_controls_effectiveness": "Effective",
  "detective_controls_description": "Monitoring and alerting systems",
  "corrective_controls_coverage": "Adequate",
  "corrective_controls_effectiveness": "Effective",
  "corrective_controls_description": "Incident response procedures",
  "risk_owner": "Test Owner",
  "risk_owner_department": "Engineering",
  "systems_affected": "Test System",
  "technology_domain": "Software Development",
  "ibs_affected": "None",
  "business_disruption_impact_rating": "Low",
  "business_disruption_impact_description": "Minimal impact to operations",
  "business_disruption_likelihood_rating": "Remote",
  "business_disruption_likelihood_description": "Very unlikely to occur",
  "financial_impact_low": 1000,
  "financial_impact_high": 5000,
  "financial_impact_notes": "Estimated cost of mitigation",
  "date_identified": "2024-01-15",
  "last_reviewed": "2024-01-15",
  "next_review_date": "2024-07-15"
}'

if make_request "POST" "/risks/" "$CREATE_RISK_DATA" "Creating test risk"; then
    # Extract risk ID from response
    RISK_ID=$(echo "$body" | grep -o '"id"[^,}]*' | cut -d'"' -f4 | head -1)
    if [ -z "$RISK_ID" ]; then
        if command -v jq &> /dev/null; then
            RISK_ID=$(echo "$body" | jq -r '.id // .risk_id // empty' 2>/dev/null)
        fi
    fi

    if [ -z "$RISK_ID" ]; then
        echo -e "${RED}✗ Could not extract risk ID from response${NC}"
        echo "Response body:"
        echo "$body"
        exit 1
    fi

    echo -e "  ${GREEN}Created risk with ID: $RISK_ID${NC}"
else
    echo -e "${RED}✗ Failed to create risk. Aborting test.${NC}"
    exit 1
fi

echo ""

# Step 2: Update the risk
echo -e "${YELLOW}Step 2: Updating the test risk${NC}"
UPDATE_RISK_DATA='{
  "risk_title": "API Test Risk (Updated)",
  "risk_description": "This test risk has been updated by the /test-api command",
  "risk_status": "Under Review",
  "planned_mitigations": "Enhanced monitoring and testing procedures"
}'

if make_request "PUT" "/risks/$RISK_ID" "$UPDATE_RISK_DATA" "Updating test risk"; then
    echo -e "  ${GREEN}Successfully updated risk $RISK_ID${NC}"
else
    echo -e "${YELLOW}⚠️  Failed to update risk, but continuing with test...${NC}"
fi

echo ""

# Step 3: Create a risk log entry
echo -e "${YELLOW}Step 3: Creating a risk log entry${NC}"
CREATE_LOG_ENTRY_DATA='{
  "field_changed": "risk_status",
  "old_value": "Active",
  "new_value": "Under Review",
  "change_reason": "Updated during API testing",
  "changed_by": "API Test Command"
}'

if make_request "POST" "/risks/$RISK_ID/log-entries" "$CREATE_LOG_ENTRY_DATA" "Creating risk log entry"; then
    # Extract log entry ID from response
    if command -v jq &> /dev/null; then
        LOG_ENTRY_ID=$(echo "$body" | jq -r '.id // .log_entry_id // empty' 2>/dev/null)
    fi
    if [ -z "$LOG_ENTRY_ID" ]; then
        LOG_ENTRY_ID=$(echo "$body" | grep -o '"id"[^,}]*' | cut -d'"' -f4 | head -1)
    fi

    if [ -n "$LOG_ENTRY_ID" ]; then
        echo -e "  ${GREEN}Created log entry with ID: $LOG_ENTRY_ID${NC}"
    else
        echo -e "  ${GREEN}Created log entry successfully${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Failed to create log entry, but continuing with test...${NC}"
fi

echo ""

# Step 4: Get the risk to verify updates
echo -e "${YELLOW}Step 4: Retrieving the updated risk${NC}"
if make_request "GET" "/risks/$RISK_ID" "" "Getting updated risk details"; then
    echo -e "  ${GREEN}Successfully retrieved risk details${NC}"
else
    echo -e "${YELLOW}⚠️  Failed to retrieve risk details${NC}"
fi

echo ""

# Step 5: Clean up - Delete the risk
echo -e "${YELLOW}Step 5: Cleaning up - Deleting the test risk${NC}"
if make_request "DELETE" "/risks/$RISK_ID" "" "Deleting test risk"; then
    echo -e "  ${GREEN}Successfully deleted test risk${NC}"
else
    echo -e "${RED}✗ Failed to delete test risk. You may need to clean it up manually.${NC}"
    echo -e "  Risk ID: $RISK_ID"
fi

echo ""
echo "🎉 API test workflow completed!"
echo ""

# Summary
echo -e "${BLUE}📊 Test Summary:${NC}"
echo "  Environment: $ENV_TYPE"
echo "  Base URL: $BASE_URL"
echo "  Risk ID tested: $RISK_ID"
if [ -n "$LOG_ENTRY_ID" ]; then
    echo "  Log Entry ID created: $LOG_ENTRY_ID"
fi
echo ""
echo "✅ The API test workflow exercises the core CRUD operations:"
echo "   • POST /risks/ - Create risk"
echo "   • PUT /risks/{id} - Update risk"
echo "   • POST /risks/{id}/log-entries - Create log entry"
echo "   • GET /risks/{id} - Retrieve risk"
echo "   • DELETE /risks/{id} - Delete risk"
```