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
    xvfb

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

# Run with xvfb for headless Chrome operation
CMD ["xvfb-run", "-a", "gunicorn", "-b", "0.0.0.0:8080", "app:app"] 