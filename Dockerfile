# Use Python 3.9 as base image
FROM python:3.9-slim

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy minimal app first
COPY minimal.py .

# Install minimal dependencies
RUN pip install --no-cache-dir flask==2.2.5 gunicorn==21.2.0

# Simple startup command with no additional complexity
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 minimal:app 