from flask import Blueprint, request, jsonify
from models import db, Resume, Questionnaire

questionnaires_bp = Blueprint('questionnaires', __name__, url_prefix='/api/questionnaires')

@questionnaires_bp.route('/<int:resume_id>', methods=['POST'])
def submit_questionnaire(resume_id):
    """Accept JSON or form-data questionnaire without CSRF/Flask-WTF."""
    data = request.get_json(silent=True) or request.form

    required = ['current_status', 'job_type', 'salary_expectation', 'preferred_location']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    resume = Resume.query.get_or_404(resume_id)

    questionnaire = Questionnaire(
        resume_id=resume_id,
        current_status=data['current_status'],
        job_type=data['job_type'],
        salary_expectation=data['salary_expectation'],
        preferred_location=data['preferred_location']
    )
    db.session.add(questionnaire)
    db.session.commit()

    return jsonify({'message': 'Questionnaire submitted successfully'})

@questionnaires_bp.route('/<int:resume_id>', methods=['GET'])
def get_questionnaire(resume_id):
    questionnaire = Questionnaire.query.filter_by(resume_id=resume_id).first_or_404()
    return jsonify({
        'current_status': questionnaire.current_status,
        'job_type': questionnaire.job_type,
        'salary_expectation': questionnaire.salary_expectation,
        'preferred_location': questionnaire.preferred_location,
        'created_at': questionnaire.created_at.isoformat()
    })
