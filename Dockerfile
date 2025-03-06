# Use Python 3.9 as base image
FROM python:3.9-slim

# Add environment variable to force Chrome to use headless mode
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV CHROME_HEADLESS=1 
ENV SELENIUM_HEADLESS=1

# Install Chrome dependencies - reduced set
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    libglib2.0-0 \
    libnss3 \
    libx11-6 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libappindicator1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    x11-apps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Create directory for screenshots and data
RUN mkdir -p app/static/screenshots
RUN mkdir -p data

# Create a diagnostic script to verify Chrome installation
RUN echo '#!/bin/bash\n\
echo "Checking Chrome installation..."\n\
which google-chrome\n\
google-chrome --version\n\
echo "Chrome is installed. Checking Python environment..."\n\
python -c "import selenium; print(f\"Selenium version: {selenium.__version__}\")"\n\
python -c "from selenium import webdriver; from selenium.webdriver.chrome.options import Options; print(\"Webdriver imports work.\")"\n\
echo "Starting Flask application..."\n\
exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 300 app:app\n' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"] 