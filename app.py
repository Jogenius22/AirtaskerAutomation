import os
import sys
import logging
from flask import Flask, render_template, jsonify
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("airtasker")

# Create the app
logger.info("Initializing app...")
app = create_app()

# Add a health check endpoint
@app.route('/_ah/health')
@app.route('/health')
@app.route('/_ah/warmup')
def health_check():
    """Health check endpoint for Cloud Run."""
    logger.info("Health check endpoint called")
    return jsonify({"status": "ok"})

# Add a root endpoint if none exists
@app.route('/')
def root():
    """Root endpoint to verify the app is working."""
    logger.info("Root endpoint called")
    return "Airtasker Automation Service is running!"

if __name__ == '__main__':
    # Get port from environment variable or default to 8080
    port = int(os.environ.get('PORT', 8080))
    # Run the app, binding to all interfaces (0.0.0.0)
    logger.info(f"Starting the app on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False) 