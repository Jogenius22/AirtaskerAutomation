# Use Python 3.9 as base image
FROM python:3.9-slim

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies but exclude selenium and related packages
RUN pip install --no-cache-dir flask==2.2.5 flask-wtf==1.2.1 python-dotenv==1.0.1 \
    werkzeug==2.2.3 wtforms==3.1.2 gunicorn==21.2.0 waitress==3.0.2 \
    requests==2.32.3 Pillow==10.2.0

# Copy the application code
COPY app/__init__.py app/
COPY app/forms.py app/
COPY app/routes.py app/
COPY app/data_manager.py app/
COPY app/tasks.py app/
COPY app/templates/ app/templates/
COPY app/static/ app/static/
COPY config.py .
COPY app.py .
COPY run.py .

# Create directory for data files
RUN mkdir -p data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DISABLE_AUTOMATION=true

# Start the Flask app with gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app 