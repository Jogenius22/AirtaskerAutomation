# Use Python 3.11 as base image
FROM python:3.11-slim

# Add environment variable to force Chrome to use headless mode
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV CHROME_HEADLESS=1 
ENV SELENIUM_HEADLESS=1

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    xvfb \
    unzip \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    libxshmfence1 \
    xdg-utils \
    procps \
    psmisc \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
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

# Create directories needed for Chrome and Xvfb
RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix \
    && mkdir -p /tmp/chrome && chmod 777 /tmp/chrome \
    && mkdir -p /dev/shm && chmod 777 /dev/shm

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1
ENV SELENIUM_HEADLESS=true
ENV PORT=8080
# Chrome flags for better extension support
ENV CHROME_ARGS="--no-sandbox --disable-dev-shm-usage --disable-gpu --disable-web-security --allow-running-insecure-content --window-size=1280,800 --remote-debugging-port=9222 --memory-pressure-off --disable-extensions"
# Set HOME directory for Chrome
ENV HOME=/tmp/chrome
# Use a lower memory ceiling for Chrome to prevent OOM issues
ENV PYTHONIOENCODING=utf-8
ENV MALLOC_TRIM_THRESHOLD_=100000
ENV MALLOC_ARENA_MAX=2

# Create a comprehensive startup script with proper error handling
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Print environment for debugging\n\
echo "Starting container with:"\n\
echo "- Display: $DISPLAY"\n\
echo "- Chrome args: $CHROME_ARGS"\n\
\n\
# Enable memory trimming\n\
echo 1 > /proc/sys/vm/overcommit_memory || echo "Warning: Could not set overcommit_memory (expected in some environments)"\n\
\n\
# Ensure data directories exist and have correct permissions\n\
mkdir -p app/static/screenshots data\n\
chmod -R 777 app/static/screenshots data\n\
ls -la app/static/screenshots data\n\
echo "✅ Directory structure verified"\n\
\n\
# Aggressively clean up any existing Chrome processes\n\
echo "Cleaning up any existing Chrome processes..."\n\
pkill -9 chrome || true\n\
pkill -9 Xvfb || true\n\
killall -9 chrome || true\n\
killall -9 chromedriver || true\n\
echo "✅ Process cleanup completed"\n\
\n\
# Clear all Chrome cache directories\n\
echo "Clearing Chrome cache directories..."\n\
rm -rf /tmp/chrome/* /tmp/.org.chromium.Chromium* /tmp/.com.google.Chrome* 2>/dev/null || true\n\
rm -rf /dev/shm/* 2>/dev/null || true\n\
# Recreate the directories with proper permissions\n\
mkdir -p /tmp/chrome\n\
chmod -R 777 /tmp/chrome\n\
mkdir -p /tmp/.X11-unix\n\
chmod 1777 /tmp/.X11-unix\n\
echo "✅ Chrome directories prepared"\n\
\n\
# Start virtual display with standard resolution\n\
echo "Starting Xvfb virtual display on $DISPLAY"\n\
Xvfb $DISPLAY -screen 0 1280x800x24 -ac +extension GLX +render -noreset > /dev/null 2>&1 &\n\
XVFB_PID=$!\n\
\n\
# Verify Xvfb is running\n\
sleep 2\n\
if ! ps -p $XVFB_PID > /dev/null; then\n\
    echo "❌ ERROR: Xvfb failed to start!"\n\
    exit 1\n\
fi\n\
echo "✅ Xvfb started successfully (PID: $XVFB_PID)"\n\
\n\
# Test Chrome can launch in headless mode with lower timeout\n\
echo "Testing Chrome launch..."\n\
timeout 5s google-chrome --headless=new --disable-gpu --no-sandbox --disable-dev-shm-usage about:blank > /dev/null 2>&1 || echo "Chrome test completed with timeout (expected)"\n\
echo "✅ Chrome test completed"\n\
\n\
# Print memory information\n\
echo "Memory information:"\n\
free -m || echo "free command not available"\n\
\n\
# Start the Flask application with gunicorn\n\
echo "Starting Flask application with Gunicorn"\n\
exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 300 app:app\n\
' > /app/startup.sh \
    && chmod +x /app/startup.sh

# Command to run
CMD ["/app/startup.sh"] 