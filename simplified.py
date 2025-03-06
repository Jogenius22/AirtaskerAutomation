import os
import sys
import traceback
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, Blueprint
import datetime
import json

# Simple data storage - no database required
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/data')
os.makedirs(DATA_DIR, exist_ok=True)

# Create a Flask app
app = Flask(__name__, 
           template_folder="app/templates",
           static_folder="app/static")
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.debug = True

# Log app startup
print(f"Starting simplified app with DATA_DIR: {DATA_DIR}", file=sys.stderr)
print(f"Template folder: {app.template_folder}", file=sys.stderr)
print(f"Static folder: {app.static_folder}", file=sys.stderr)

# Register error handlers
@app.errorhandler(500)
def server_error(e):
    tb = traceback.format_exception(*sys.exc_info())
    error_details = {
        "error": str(e),
        "traceback": tb,
        "endpoint": request.endpoint,
        "url": request.url
    }
    print(f"500 Error: {error_details}", file=sys.stderr)
    return jsonify(error_details), 500

# Data access functions
def get_data(filename, default=None):
    """Get data from a JSON file"""
    if default is None:
        default = []
    filepath = os.path.join(DATA_DIR, f"{filename}.json")
    if not os.path.exists(filepath):
        print(f"Warning: Data file {filepath} does not exist. Returning default.", file=sys.stderr)
        return default
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            print(f"Loaded data from {filepath}: {data}", file=sys.stderr)
            return data
    except Exception as e:
        print(f"Error loading {filepath}: {str(e)}", file=sys.stderr)
        return default

def save_data(filename, data):
    """Save data to a JSON file"""
    filepath = os.path.join(DATA_DIR, f"{filename}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

# Routes
@app.route('/')
def dashboard():
    """Dashboard page with basic info"""
    try:
        # Get sample data with detailed logging
        print("Dashboard route accessed", file=sys.stderr)
        accounts = get_data('accounts', [])
        print(f"Accounts: {accounts}", file=sys.stderr)
        
        cities = get_data('cities', [])
        print(f"Cities: {cities}", file=sys.stderr)
        
        messages = get_data('messages', [])
        print(f"Messages: {messages}", file=sys.stderr)
        
        logs_data = get_data('logs', {'items': [], 'page': 1, 'per_page': 5, 'total': 0})
        logs = logs_data.get('items', [])
        print(f"Logs: {logs}", file=sys.stderr)
        
        # Try with a simpler approach first
        try:
            # First try to render a super simple template to ensure the template engine works
            print("Attempting to render simple template", file=sys.stderr)
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Simple Dashboard</title>
            </head>
            <body>
                <h1>Dashboard is working!</h1>
                <p>This is a simple version of the dashboard without using templates.</p>
                <h2>Accounts:</h2>
                <pre>{}</pre>
                <h2>Cities:</h2>
                <pre>{}</pre>
                <h2>Messages:</h2>
                <pre>{}</pre>
                <h2>Logs:</h2>
                <pre>{}</pre>
            </body>
            </html>
            """.format(
                json.dumps(accounts, indent=2),
                json.dumps(cities, indent=2),
                json.dumps(messages, indent=2),
                json.dumps(logs, indent=2)
            )
        except Exception as inner_e:
            print(f"Error rendering simple HTML: {str(inner_e)}", file=sys.stderr)
            raise
        
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK'

@app.route('/api/status')
def api_status():
    """API endpoint for app status"""
    return jsonify({
        "status": "ok",
        "app_version": "simplified",
        "timestamp": datetime.datetime.now().isoformat(),
        "template_folder": app.template_folder,
        "static_folder": app.static_folder
    })

@app.route('/simple-dashboard')
def simple_dashboard():
    """A very simple dashboard with minimal template requirements"""
    accounts = get_data('accounts', [])
    cities = get_data('cities', [])
    messages = get_data('messages', [])
    logs_data = get_data('logs', {'items': [], 'page': 1, 'per_page': 5, 'total': 0})
    
    return jsonify({
        "title": "Simple Dashboard",
        "accounts": accounts,
        "cities": cities,
        "messages": messages,
        "logs": logs_data.get('items', [])
    })

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True) 