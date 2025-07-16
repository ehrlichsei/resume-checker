from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resumes = relationship('Resume', backref='user', lazy=True)
    payments = relationship('Payment', backref='user', lazy=True)

class Resume(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    slug = Column(String(16), unique=True, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    analysis = Column(JSON)
    questionnaire = relationship('Questionnaire', backref='resume', uselist=False)

class Questionnaire(db.Model):
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resume.id'), nullable=False)
    current_status = Column(String(50))
    job_type = Column(String(50))
    salary_expectation = Column(String(50))
    preferred_location = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    payment_intent_id = Column(String(100), unique=True, nullable=False)
    amount = Column(Integer, nullable=False)  # in cents
    currency = Column(String(3), nullable=False)
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

# The SQLAlchemy `db` object will be initialized with the main Flask app in app.py.
