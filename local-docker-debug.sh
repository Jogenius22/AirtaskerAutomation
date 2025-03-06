#!/bin/bash
# Script to build and run the Docker container locally

echo "=== Building Docker container ==="
docker build -t airtasker-app:debug .

echo "=== Running Docker container ==="
echo "The app will be available at http://localhost:8080"
docker run --rm -p 8080:8080 --name airtasker-debug airtasker-app:debug

# To view logs in another terminal, you can use:
# docker logs -f airtasker-debug 