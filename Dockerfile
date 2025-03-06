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
    netcat-openbsd \
    supervisor

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
ENV DISPLAY=:99

# Create a supervisord configuration to manage processes
RUN echo '[supervisord]\n\
nodaemon=true\n\
\n\
[program:xvfb]\n\
command=Xvfb :99 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset\n\
priority=10\n\
autorestart=true\n\
\n\
[program:gunicorn]\n\
command=gunicorn --bind :8080 --workers 1 --threads 8 --timeout 120 app:app\n\
priority=20\n\
directory=/app\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
autorestart=true\n\
startretries=5\n' > /etc/supervisor/conf.d/supervisord.conf

# Create a simplified startup script
RUN echo '#!/bin/bash\n\
echo "Starting supervisor..."\n\
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf\n' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"] 