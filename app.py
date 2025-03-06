import os
import sys
import traceback
from flask import Flask, render_template, jsonify, request
from app import create_app

app = create_app()

# Add a health check endpoint
@app.route('/_ah/health')
@app.route('/health')
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({"status": "ok"})

# Add a debug route
@app.route('/debug')
def debug():
    """Debug endpoint to check if Flask is running correctly."""
    debug_info = {
        "flask_env": os.environ.get('FLASK_ENV', 'not set'),
        "flask_debug": os.environ.get('FLASK_DEBUG', 'not set'),
        "port": os.environ.get('PORT', 'not set'),
        "python_path": os.environ.get('PYTHONPATH', 'not set'),
        "app_directory": os.path.dirname(os.path.abspath(__file__)),
        "working_directory": os.getcwd()
    }
    
    # Try to import selenium to check if it's working
    try:
        import selenium
        debug_info["selenium_version"] = selenium.__version__
        debug_info["selenium_status"] = "imported successfully"
    except Exception as e:
        debug_info["selenium_status"] = f"import failed: {str(e)}"
    
    # Check if Chrome is installed
    try:
        import subprocess
        chrome_version = subprocess.check_output(["google-chrome", "--version"]).decode().strip()
        debug_info["chrome_version"] = chrome_version
    except Exception as e:
        debug_info["chrome_version"] = f"check failed: {str(e)}"
    
    return jsonify(debug_info)

# Add an error handler for 500 errors
@app.errorhandler(500)
def server_error(e):
    """Handle internal server errors with detailed debugging information."""
    # Get the traceback
    tb = traceback.format_exception(*sys.exc_info())
    
    # Create a detailed error response
    error_details = {
        "error": str(e),
        "traceback": tb,
        "endpoint": request.endpoint,
        "url": request.url,
        "method": request.method,
        "remote_addr": request.remote_addr,
        "user_agent": str(request.user_agent)
    }
    
    # Log the error
    print(f"500 Error: {error_details}", file=sys.stderr)
    
    # Return a JSON response in debug mode, or a simple message in production
    if app.debug:
        return jsonify(error_details), 500
    else:
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 8080
    port = int(os.environ.get('PORT', 8080))
    # Run the app, binding to all interfaces (0.0.0.0)
    app.run(host='0.0.0.0', port=port, debug=True) 