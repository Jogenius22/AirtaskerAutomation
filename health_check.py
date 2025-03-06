#!/usr/bin/env python3
"""
Simple health check server that runs separately from the main app
to help Cloud Run determine if the container is healthy.
"""
import os
import http.server
import socketserver

PORT = int(os.getenv('PORT', '8081'))  # Use a different port than main app

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        return

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        print(f"Health check server running at port {PORT}")
        httpd.serve_forever() 