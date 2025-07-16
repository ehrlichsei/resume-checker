from flask import Blueprint, request, jsonify
from models import db, User, Payment
from payment_processor import PaymentProcessor

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@payments_bp.route('/create', methods=['POST'])
def create_payment():
    try:
        resume_id = request.json.get('resume_id')
        if not resume_id:
            return jsonify({'error': 'resume_id is required'}), 400

        # Get or create user (assuming user is authenticated)
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(email='test@example.com')
            db.session.add(user)
            db.session.commit()

        # Create payment intent
        payment_processor = PaymentProcessor()
        payment_intent = payment_processor.create_payment_intent(
            amount=100,  # $1.00 in cents
            currency='usd',
            user_id=user.id
        )

        return jsonify({
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/confirm', methods=['POST'])
def confirm_payment():
    try:
        payment_intent_id = request.json.get('payment_intent_id')
        payment_method_id = request.json.get('payment_method_id')
        resume_id = request.json.get('resume_id')

        if not all([payment_intent_id, payment_method_id, resume_id]):
            return jsonify({'error': 'Missing required parameters'}), 400

        # Confirm payment
        payment_processor = PaymentProcessor()
        payment = payment_processor.confirm_payment(
            payment_intent_id=payment_intent_id,
            payment_method_id=payment_method_id
        )

        # Update payment record in database
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        payment_record = Payment(
            user_id=user.id,
            payment_intent_id=payment_intent_id,
            amount=100,  # $1.00 in cents
            currency='usd',
            status=payment.status
        )
        db.session.add(payment_record)
        db.session.commit()

        return jsonify({
            'success': True,
            'payment_status': payment.status
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
