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

# Initialize sample data if files don't exist
def create_sample_data():
    # Sample accounts
    accounts = [
        {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "status": "active",
            "created_at": "2023-01-01T12:00:00Z"
        },
        {
            "id": 2,
            "username": "demouser",
            "email": "demo@example.com",
            "status": "active",
            "created_at": "2023-01-02T10:30:00Z"
        }
    ]
    
    # Sample cities
    cities = [
        {
            "id": 1,
            "name": "Sydney",
            "country": "Australia",
            "coordinates": {
                "lat": -33.8688,
                "lng": 151.2093
            }
        },
        {
            "id": 2,
            "name": "Melbourne",
            "country": "Australia",
            "coordinates": {
                "lat": -37.8136,
                "lng": 144.9631
            }
        },
        {
            "id": 3,
            "name": "Brisbane",
            "country": "Australia",
            "coordinates": {
                "lat": -27.4698,
                "lng": 153.0251
            }
        }
    ]
    
    # Sample messages
    messages = [
        {
            "id": 1,
            "user_id": 1,
            "content": "Hey did you know there is another jobs application called SmartTasker with less fees. You are more likely to get better quotes.",
            "posted_at": "2023-03-01T09:15:00Z",
            "task_id": "t123"
        },
        {
            "id": 2,
            "user_id": 2,
            "content": "Hi for this task you might want to post on SmartTasker. The fees are less so we can give you better quotes",
            "posted_at": "2023-03-02T14:30:00Z",
            "task_id": "t456"
        },
        {
            "id": 3,
            "user_id": 1,
            "content": "By the way you might get better quotes with posting to the SmartTasker application. Better fees for all users and more options.",
            "posted_at": "2023-03-03T11:45:00Z",
            "task_id": "t789"
        }
    ]
    
    # Sample logs
    logs = {
        "items": [
            {
                "id": 1,
                "timestamp": "2023-03-05T08:00:00Z",
                "level": "INFO",
                "message": "Application started successfully"
            },
            {
                "id": 2,
                "timestamp": "2023-03-05T08:15:30Z",
                "level": "INFO",
                "message": "User login: testuser"
            },
            {
                "id": 3,
                "timestamp": "2023-03-05T09:20:15Z",
                "level": "WARNING",
                "message": "Rate limit approached for task scraping"
            },
            {
                "id": 4,
                "timestamp": "2023-03-05T10:05:45Z",
                "level": "INFO",
                "message": "Successfully posted 3 comments"
            },
            {
                "id": 5,
                "timestamp": "2023-03-05T11:30:00Z",
                "level": "INFO",
                "message": "User logout: testuser"
            }
        ],
        "page": 1,
        "per_page": 5,
        "total": 5
    }
    
    # Save sample data
    if not os.path.exists(os.path.join(DATA_DIR, "accounts.json")):
        save_data("accounts", accounts)
        print("Created sample accounts data", file=sys.stderr)
        
    if not os.path.exists(os.path.join(DATA_DIR, "cities.json")):
        save_data("cities", cities)
        print("Created sample cities data", file=sys.stderr)
        
    if not os.path.exists(os.path.join(DATA_DIR, "messages.json")):
        save_data("messages", messages)
        print("Created sample messages data", file=sys.stderr)
        
    if not os.path.exists(os.path.join(DATA_DIR, "logs.json")):
        save_data("logs", logs)
        print("Created sample logs data", file=sys.stderr)

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
            print(f"Loaded data from {filepath}: {str(data)[:100]}...", file=sys.stderr)
            return data
    except Exception as e:
        print(f"Error loading {filepath}: {str(e)}", file=sys.stderr)
        return default

def save_data(filename, data):
    """Save data to a JSON file"""
    filepath = os.path.join(DATA_DIR, f"{filename}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved data to {filepath}", file=sys.stderr)

# Routes
@app.route('/')
def dashboard():
    """Dashboard page with basic info"""
    try:
        # Get sample data with detailed logging
        print("Dashboard route accessed", file=sys.stderr)
        accounts = get_data('accounts', [])
        print(f"Accounts count: {len(accounts)}", file=sys.stderr)
        
        cities = get_data('cities', [])
        print(f"Cities count: {len(cities)}", file=sys.stderr)
        
        messages = get_data('messages', [])
        print(f"Messages count: {len(messages)}", file=sys.stderr)
        
        logs_data = get_data('logs', {'items': [], 'page': 1, 'per_page': 5, 'total': 0})
        logs = logs_data.get('items', [])
        print(f"Logs count: {len(logs)}", file=sys.stderr)
        
        # Try with a simpler approach first
        try:
            # First try to render a super simple template to ensure the template engine works
            print("Attempting to render simple template", file=sys.stderr)
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Simple Dashboard</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                    h1 { color: #333; }
                    pre { background: #f5f5f5; padding: 10px; overflow: auto; }
                </style>
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
    # Create sample data on startup
    create_sample_data()
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True) 