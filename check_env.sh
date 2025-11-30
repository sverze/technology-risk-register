#!/bin/bash
# Script to verify environment setup for Technology Risk Register

echo "=================================="
echo "Environment Setup Verification"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found"
    echo ""
    echo "To fix this:"
    echo "  1. Copy the example file: cp .env.example .env"
    echo "  2. Edit .env and add your Anthropic API key"
    echo "  3. See ENV_SETUP.md for detailed instructions"
    echo ""
    exit 1
else
    echo "✓ .env file found"
fi

# Check if ANTHROPIC_API_KEY is set in .env
if grep -q "ANTHROPIC_API_KEY=.*" .env && ! grep -q "ANTHROPIC_API_KEY=your_anthropic_api_key_here" .env; then
    echo "✓ ANTHROPIC_API_KEY is set in .env"

    # Check if it looks like a valid key format
    if grep -q "ANTHROPIC_API_KEY=sk-ant-" .env; then
        echo "✓ ANTHROPIC_API_KEY format looks correct"
    else
        echo "⚠ WARNING: ANTHROPIC_API_KEY format may be incorrect"
        echo "  Expected format: sk-ant-api03-..."
    fi
else
    echo "❌ ERROR: ANTHROPIC_API_KEY not set or using placeholder value"
    echo ""
    echo "To fix this:"
    echo "  1. Get your API key from https://console.anthropic.com/settings/keys"
    echo "  2. Edit .env and replace 'your_anthropic_api_key_here' with your actual key"
    echo ""
    exit 1
fi

# Check if Docker is running
if docker info > /dev/null 2>&1; then
    echo "✓ Docker is running"
else
    echo "⚠ WARNING: Docker is not running"
    echo "  You'll need Docker to run the containerized application"
fi

# Check if docker-compose.yml exists
if [ -f docker-compose.yml ]; then
    echo "✓ docker-compose.yml found"
else
    echo "❌ ERROR: docker-compose.yml not found"
    exit 1
fi

# Check other required environment variables
echo ""
echo "Checking other environment variables in .env:"

required_vars=("DATABASE_URL" "AUTH_USERNAME" "AUTH_PASSWORD" "AUTH_SECRET_KEY")
for var in "${required_vars[@]}"; do
    if grep -q "$var=.*" .env; then
        echo "  ✓ $var is set"
    else
        echo "  ⚠ WARNING: $var not found in .env (will use default)"
    fi
done

echo ""
echo "=================================="
echo "✅ Environment setup looks good!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Start the application: docker-compose up -d"
echo "  2. Check logs: docker-compose logs -f backend"
echo "  3. Access the app:"
echo "     - Frontend: http://localhost:3000"
echo "     - Backend API: http://localhost:8080/docs"
echo "     - Risk Chat: http://localhost:3000/chat"
echo ""
echo "To verify the API key is working:"
echo "  docker-compose exec backend printenv | grep ANTHROPIC_API_KEY"
echo ""
