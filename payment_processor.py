import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class PaymentProcessor:
    def create_payment_intent(self, amount, currency):
        """
        Create a Stripe Payment Intent
        
        Args:
            amount (int): Amount in cents
            currency (str): Currency code (e.g., 'usd')
            
        Returns:
            dict: Payment intent details
        """
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method_types=['card']
            )
            return payment_intent
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
            
    def confirm_payment(self, payment_intent_id, payment_method_id):
        """
        Confirm a payment
        
        Args:
            payment_intent_id (str): Stripe payment intent ID
            payment_method_id (str): Stripe payment method ID
            
        Returns:
            dict: Confirmation details
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method_id
            )
            return payment_intent
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
