# Use Python 3.9 as base image
FROM python:3.9-slim

# Install Chrome and its dependencies (updated method)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    xvfb \
    netcat-openbsd

# Install Google Chrome (updated approach)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for screenshots if it doesn't exist
RUN mkdir -p app/static/screenshots

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV GUNICORN_CMD_ARGS="--timeout 120 --workers 1 --threads 8 --bind 0.0.0.0:8080"

# Create a simpler startup script for Cloud Run
RUN echo '#!/bin/bash\n\
# Start Xvfb in the background\n\
Xvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 &\n\
export DISPLAY=:99\n\
\n\
# Start the application with gunicorn\n\
exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 120 app:app\n' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"] 