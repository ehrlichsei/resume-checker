from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv
import os
import sys
from blueprints import blueprints
from models import db

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

# Initialize Swagger for automatic API documentation
swagger = Swagger(app, template={
    "info": {
        "title": "Resume Analyzer API",
        "version": "1.0",
        "description": "Endpoints for uploading resumes, analyzing, and retrieving results."
    }
})

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_analyzer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize SQLAlchemy
db.init_app(app)

# Create tables if they do not exist
with app.app_context():
    db.create_all()

# Register blueprints
for bp in blueprints:
    app.register_blueprint(bp)

# Configure OpenAI
try:
    import openai
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    print("OpenAI API key configured successfully")
except Exception as e:
    print(f"Error configuring OpenAI: {str(e)}")

@app.route('/')
def index():
    return app.send_static_file('index.html')

# Catch-all to support client-side routing (React Router)
# Any 404 that is NOT an API nor static asset should return index.html so the
# frontend can handle the route, avoiding blank 404 pages on refresh or direct
# link (e.g. /results/123).
@app.errorhandler(404)
def spa_fallback(e):
    if request.path.startswith('/api') or request.path.startswith('/uploads'):
        # Real 404 for API or upload resources
        return jsonify({'error': 'Not found'}), 404
    # Otherwise serve the SPA entrypoint
    return app.send_static_file('index.html')

if __name__ == '__main__':
    # Get port from environment variable with fallback to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Print diagnostic information for debugging
    print(f"Starting server on port {port}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Run the Flask application (development server)
    app.run(host="0.0.0.0", port=port, debug=True)
