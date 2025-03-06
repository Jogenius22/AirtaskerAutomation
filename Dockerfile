# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY simplified.py .
COPY app/ app/

# Create data directory and ensure it's accessible
RUN mkdir -p app/data
COPY app/data/*.json app/data/

# Expose the port the app runs on
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV CHROME_HEADLESS=true

# Run the application
CMD ["python", "simplified.py"] 