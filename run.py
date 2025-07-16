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
    app.run(debug=True)
