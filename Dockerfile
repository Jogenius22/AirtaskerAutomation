# Use Python 3.9 as base image
FROM python:3.9-slim

# Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    libglib2.0-0 \
    libnss3 \
    libx11-6 \
    libx11-xcb1 \
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
    libappindicator1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libgconf-2-4 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    xvfb \
    fonts-liberation \
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

# Create directory for screenshots
RUN mkdir -p app/static/screenshots

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DISPLAY=:99

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Xvfb with logging\n\
echo "Starting Xvfb..."\n\
Xvfb :99 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset &\n\
echo "Xvfb started. Sleeping for 10 seconds..."\n\
sleep 10\n\
echo "Starting Gunicorn..."\n\
exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 120 app:app\n' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"] 