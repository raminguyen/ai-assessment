#!/bin/bash
# Simple HTTP server to serve the AI Assessment application
# Run this script from the project root directory

echo "Starting HTTP server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
python3 -m http.server 8000
