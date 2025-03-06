import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
import datetime
import json

# Simple data storage - no database required
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Create a Flask app
app = Flask(__name__, 
           template_folder="app/templates",
           static_folder="app/static")
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# Data access functions
def get_data(filename, default=None):
    """Get data from a JSON file"""
    if default is None:
        default = []
    filepath = os.path.join(DATA_DIR, f"{filename}.json")
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
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
    # Get some basic data
    accounts = get_data('accounts', [])
    cities = get_data('cities', [])
    messages = get_data('messages', [])
    logs = get_data('logs', {'items': [], 'page': 1, 'per_page': 5, 'total': 0})
    
    return render_template('dashboard.html', 
                          accounts=accounts,
                          cities=cities,
                          messages=messages,
                          logs=logs.get('items', []))

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

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True) 