from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange

class ResumeForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    resume = StringField('Resume', validators=[DataRequired()])
    submit = SubmitField('Upload Resume')

class QuestionnaireForm(FlaskForm):
    current_status = SelectField('Current Employment Status', choices=[
        ('employed', 'Currently Employed'),
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    job_type = SelectField('Preferred Job Type', choices=[
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid')
    ], validators=[DataRequired()])
    
    salary_expectation = FloatField('Salary Expectation (USD)', validators=[
        DataRequired(),
        NumberRange(min=0, message='Please enter a valid salary expectation')
    ])
    
    preferred_location = StringField('Preferred Location', validators=[DataRequired()])
    submit = SubmitField('Submit Questionnaire')
