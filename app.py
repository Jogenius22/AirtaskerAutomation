import os
from flask import Flask, render_template, jsonify
from app import create_app

# Add environment variable check for disabling automation
if os.environ.get('DISABLE_AUTOMATION', 'false').lower() == 'true':
    # This will be used to conditionally disable automation features
    print("Running in DISABLE_AUTOMATION mode - Selenium features disabled")
    os.environ['FLASK_ENV'] = 'production'

app = create_app()

# Add a health check endpoint
@app.route('/_ah/health')
@app.route('/health')
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # Get port from environment variable or default to 8080
    port = int(os.environ.get('PORT', 8080))
    # Run the app, binding to all interfaces (0.0.0.0)
    app.run(host='0.0.0.0', port=port, debug=False) 