from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from forms import ResumeForm, QuestionnaireForm
from pdf_processor import PDFProcessor
from payment_processor import PaymentProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_analyzer.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resumes = db.relationship('Resume', backref='user', lazy=True)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    questionnaire = db.relationship('Questionnaire', backref='resume', uselist=False)

class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    current_status = db.Column(db.String(255))
    job_type = db.Column(db.String(255))
    salary_expectation = db.Column(db.Float)
    preferred_location = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    form = ResumeForm()
    if form.validate_on_submit():
        if 'resume' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['resume']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Create new resume entry
            new_resume = Resume(filename=filename, user_id=1)  # TODO: Implement user authentication
            db.session.add(new_resume)
            db.session.commit()
            
            flash('Resume uploaded successfully!')
            return redirect(url_for('questionnaire', resume_id=new_resume.id))
    
    return render_template('upload.html', form=form)

@app.route('/questionnaire/<int:resume_id>', methods=['GET', 'POST'])
def questionnaire(resume_id):
    form = QuestionnaireForm()
    resume = Resume.query.get_or_404(resume_id)
    
    if form.validate_on_submit():
        new_questionnaire = Questionnaire(
            resume_id=resume_id,
            current_status=form.current_status.data,
            job_type=form.job_type.data,
            salary_expectation=form.salary_expectation.data,
            preferred_location=form.preferred_location.data
        )
        db.session.add(new_questionnaire)
        db.session.commit()
        
        flash('Questionnaire submitted successfully!')
        return redirect(url_for('payment', resume_id=resume_id))
    
    return render_template('questionnaire.html', form=form)

@app.route('/payment/<int:resume_id>', methods=['GET', 'POST'])
def payment(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    payment_processor = PaymentProcessor()
    
    if request.method == 'POST':
        try:
            payment_intent = payment_processor.create_payment_intent(
                amount=1000,  # $10.00
                currency='usd'
            )
            return jsonify({
                'clientSecret': payment_intent['client_secret']
            })
        except Exception as e:
            return jsonify(error=str(e)), 403
    
    return render_template('payment.html', resume_id=resume_id)

if __name__ == '__main__':
    app.run(debug=True)
