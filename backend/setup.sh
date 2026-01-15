#!/bin/bash

echo "Setting up Social Media Tracker Backend..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please update it with your credentials."
fi

echo "Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your database URL"
echo "2. Start PostgreSQL: brew services start postgresql"
echo "3. Create database: createdb social_media_tracker"
echo "4. Run the server: python main.py"
