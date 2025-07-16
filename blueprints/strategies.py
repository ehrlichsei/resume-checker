from flask import Blueprint, request, jsonify
from models import Resume
from pdf_processor import PDFProcessor
import openai, os, json

strategies_bp = Blueprint('strategies', __name__, url_prefix='/api/strategies')

@strategies_bp.route('/<int:resume_id>', methods=['POST'])
def generate_strategy(resume_id):
    """Combine resume analysis + questionnaire to generate job-hunting strategy."""
    resume = Resume.query.get_or_404(resume_id)

    # Ensure resume analysis exists
    if not resume.processed or not resume.analysis:
        pdf_processor = PDFProcessor()
        filepath = os.path.join('uploads', resume.filename)
        resume.analysis = pdf_processor.analyze_resume(filepath)
        resume.processed = True

    if not resume.questionnaire:
        return jsonify({'error': 'Questionnaire not found for this resume'}), 400

    questionnaire_dict = {
        'current_status': resume.questionnaire.current_status,
        'job_type': resume.questionnaire.job_type,
        'salary_expectation': resume.questionnaire.salary_expectation,
        'preferred_location': resume.questionnaire.preferred_location,
    }

    try:
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        system_msg = "You are an expert career coach and labour-market analyst."
        user_prompt = (
            "Based on the following resume analysis JSON and questionnaire data, "
            "produce a JSON advice report with these keys:\n"
            "job_market_overview: short paragraph,\n"
            "personal_strategy: detailed plan (3-5 bullet points),\n"
            "recommended_job_boards: list of strings,\n"
            "next_steps: list of actionable next steps.\n\n"
            f"Resume analysis: {json.dumps(resume.analysis)}\n\n"
            f"Questionnaire: {json.dumps(questionnaire_dict)}"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "system", "content": "Return ONLY pure JSON with no markdown."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
            max_tokens=800
        )
        raw = response.choices[0].message.content.strip()
        strategy = json.loads(raw)
    except Exception as e:
        print('Strategy generation failed:', e)
        strategy = {
            'job_market_overview': 'Could not retrieve AI-generated overview. Please try again later.',
            'personal_strategy': 'N/A',
            'recommended_job_boards': [],
            'next_steps': []
        }

    return jsonify({'strategy': strategy})
