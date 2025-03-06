# Use Python 3.9 as base image
FROM python:3.9-slim

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV FLASK_DEBUG=1

# Set working directory
WORKDIR /app

# Install dependencies - just Flask and related packages, no Selenium/Chrome
RUN pip install --no-cache-dir \
    flask==2.2.5 \
    flask-wtf==1.2.1 \
    gunicorn==21.2.0 \
    python-dotenv==1.0.1 \
    werkzeug==2.2.3 \
    wtforms==3.1.2

# Copy app templates and static files
COPY app/templates/ app/templates/
COPY app/static/ app/static/

# Copy the simplified app
COPY simplified.py .

# Create data directory
RUN mkdir -p data

# Start the app with gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 simplified:app 