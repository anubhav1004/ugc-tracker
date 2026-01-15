#!/bin/bash

echo "=================================="
echo "Social Media Tracker - Full Setup"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

python_version=$(python3 --version | cut -d" " -f2)
echo -e "${GREEN}✓${NC} Python $python_version found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js 16 or higher.${NC}"
    exit 1
fi

node_version=$(node --version)
echo -e "${GREEN}✓${NC} Node.js $node_version found"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} PostgreSQL not found. Install it with: brew install postgresql"
else
    echo -e "${GREEN}✓${NC} PostgreSQL found"
fi

echo ""
echo "=================================="
echo "Setting up Backend..."
echo "=================================="

cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Install Playwright
echo "Installing Playwright browsers..."
python -m playwright install chromium

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠${NC} Please update .env with your database credentials"
fi

echo -e "${GREEN}✓${NC} Backend setup complete!"

cd ..

echo ""
echo "=================================="
echo "Setting up Frontend..."
echo "=================================="

cd frontend

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install

echo -e "${GREEN}✓${NC} Frontend setup complete!"

cd ..

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Start PostgreSQL: brew services start postgresql"
echo "2. Create database: createdb social_media_tracker"
echo "3. Update backend/.env with your database URL"
echo ""
echo "To run the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Access the app at: http://localhost:3000"
echo "API docs at: http://localhost:8000/docs"
echo ""
