from flask import Blueprint

# Import all blueprints
from blueprints.resumes import resumes_bp
from blueprints.payments import payments_bp
from blueprints.questionnaires import questionnaires_bp
from blueprints.strategies import strategies_bp

# Register all blueprints
blueprints = [
    resumes_bp,
    payments_bp,
    questionnaires_bp,
    strategies_bp
]
