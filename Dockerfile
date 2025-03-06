# Use Python 3.9 as base image
FROM python:3.9-slim

# Add environment variable to force Chrome to use headless mode
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV CHROME_HEADLESS=1 
ENV SELENIUM_HEADLESS=1
ENV GUNICORN_CMD_ARGS="--log-level debug"

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

# Create a detailed diagnostic script with more debugging
RUN echo '#!/bin/bash\n\
echo "===== SYSTEM INFO =====" > /app/debug.log\n\
uname -a >> /app/debug.log\n\
echo "" >> /app/debug.log\n\
\n\
echo "===== DIRECTORY STRUCTURE =====" >> /app/debug.log\n\
find /app -type f -name "*.py" | sort >> /app/debug.log\n\
echo "" >> /app/debug.log\n\
\n\
echo "===== CHROME INSTALLATION =====" >> /app/debug.log\n\
which google-chrome >> /app/debug.log 2>&1\n\
google-chrome --version >> /app/debug.log 2>&1\n\
echo "" >> /app/debug.log\n\
\n\
echo "===== PYTHON ENVIRONMENT =====" >> /app/debug.log\n\
python --version >> /app/debug.log 2>&1\n\
pip list >> /app/debug.log 2>&1\n\
echo "" >> /app/debug.log\n\
\n\
echo "===== TESTING SELENIUM =====" >> /app/debug.log\n\
python -c "import selenium; print(f\\"Selenium version: {selenium.__version__}\\")" >> /app/debug.log 2>&1\n\
python -c "from selenium import webdriver; from selenium.webdriver.chrome.options import Options; print(\\"Selenium imports work.\\")" >> /app/debug.log 2>&1\n\
echo "" >> /app/debug.log\n\
\n\
echo "==== CHECKING APP STRUCTURE ====" >> /app/debug.log\n\
python -c "import app; print(f\\"App imported successfully: {app.__file__}\\")" >> /app/debug.log 2>&1\n\
python -c "import flask; print(f\\"Flask version: {flask.__version__}\\")" >> /app/debug.log 2>&1\n\
\n\
echo "Debug log created at /app/debug.log"\n\
cat /app/debug.log\n\
\n\
echo "Starting Flask application with Gunicorn..."\n\
exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 300 --log-level debug app:app\n' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"] 