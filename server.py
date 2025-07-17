#!/usr/bin/env python3
import os
import sys
from app import app

if __name__ == "__main__":
    # Get port from environment variable with fallback to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Print diagnostic information
    print(f"Starting server on port {port}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Run the Flask application
    app.run(host="0.0.0.0", port=port)
