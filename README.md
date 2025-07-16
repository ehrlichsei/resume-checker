# Resume Analyzer

A modern web application that analyzes resumes using OpenAI's API and provides detailed insights about skills, experience, and education.

## Features

- Upload PDF resumes
- AI-powered resume analysis using OpenAI
- Detailed skill and experience breakdown
- Education history analysis
- Questionnaire for job preferences
- Modern React frontend with Material-UI

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:
```bash
pip install flask flask-sqlalchemy werkzeug python-dotenv openai PyPDF2
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

4. Run the backend:
```bash
python app.py
```

### Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

2. Build the frontend:
```bash
npm run build
```

3. The frontend build will be automatically served by the Flask backend.

## Running the Application

1. Ensure both backend and frontend are set up as described above.
2. Start the Flask backend:
```bash
python app.py
```
3. Open your browser and navigate to `http://localhost:5000`

## API Endpoints

- POST `/api/upload` - Upload a resume
- GET `/api/resume/:id` - Get resume analysis
- POST `/api/questionnaire/:id` - Submit questionnaire

## Project Structure

```
resume_analyzer/
├── app.py                # Flask backend
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   └── pages/       # Page components
│   └── package.json
├── uploads/              # Resume uploads
├── .env                  # Environment variables
└── requirements.txt      # Python dependencies
