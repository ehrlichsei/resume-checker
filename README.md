# Resume Analyzer Web Application

A web application for resume analysis with PDF processing, questionnaire functionality, and payment integration.

## Features

- Upload PDF resumes
- Fill out job application questionnaire
- Resume analysis and processing
- Secure payment integration
- User-friendly interface

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
   - On Windows:
   ```bash
   .\venv\Scripts\activate
   ```
   - On Unix or MacOS:
   ```bash
   source venv/bin/activate
   ```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Stripe API keys:
```
STRIPE_SECRET_KEY=your_secret_key
STRIPE_PUBLISHABLE_KEY=your_publishable_key
SECRET_KEY=your_application_secret_key
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to `http://localhost:5000`

## Project Structure

- `app.py`: Main Flask application
- `forms.py`: WTForms definitions
- `pdf_processor.py`: PDF processing and analysis
- `payment_processor.py`: Stripe payment integration
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static files
- `uploads/`: Directory for uploaded resumes

## Requirements

- Python 3.8+
- Flask
- SQLAlchemy
- Stripe API keys
- SQLite (or other supported database)

## Deactivating the Virtual Environment

To deactivate the virtual environment when you're done:
```bash
deactivate
