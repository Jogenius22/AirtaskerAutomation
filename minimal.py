import os
from flask import Flask

# Create a minimal app with no dependencies
app = Flask(__name__)

@app.route('/')
def home():
    return 'Minimal Flask app is working!'

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 