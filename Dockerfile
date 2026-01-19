FROM python:3.11-slim

WORKDIR /app

# Set Playwright browser path
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install system dependencies including those needed for Chromium
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    gnupg \
    # Chromium dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    fonts-liberation \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (without system deps since we already installed them)
RUN playwright install chromium

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Start command
CMD ["/bin/sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
