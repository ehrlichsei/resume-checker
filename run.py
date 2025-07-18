import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set environment variable for Flask
os.environ['FLASK_APP'] = 'app.py'

# Run Flask application
from app import app

if __name__ == '__main__':
    # For local development
    app.run(debug=True)
else:
    # For production deployment on Render
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    # This will be executed when imported by gunicorn
