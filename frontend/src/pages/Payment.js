import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  TextField,
  Stack,
} from '@mui/material';
import { loadStripe } from '@stripe/stripe-js';
import api from '../api';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || 'your_stripe_publishable_key_here');

const Payment = () => {
  const navigate = useNavigate();
  const { slug } = useParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [amount, setAmount] = useState(100); // $1.00
  const [debugInfo, setDebugInfo] = useState([]);
  const cardElementRef = useRef(null);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    console.log('Payment component mounted');
    fetchPaymentIntent();
  }, []); 

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (clientSecret) {
      console.log('Client secret received:', clientSecret);
      initializeStripeElements();
    }
  }, [clientSecret]); 

  const addDebugInfo = (message, data = null) => {
    setDebugInfo(prev => [
      ...prev,
      {
        timestamp: new Date().toISOString(),
        message,
        data
      }
    ]);
  };

  const fetchPaymentIntent = async () => {
    console.log('Fetching payment intent...');
    addDebugInfo('Fetching payment intent');
    try {
      const response = await api.post('/api/payment/create', {
        amount: amount,
        currency: 'usd'
      });
      const data = await response.data;
      console.log('Payment intent response:', data);
      addDebugInfo('Payment intent received', data);
      if (data.client_secret) {
        setClientSecret(data.client_secret);
      } else {
        setError('No client secret received from server');
      }
    } catch (err) {
      console.error('Payment initialization error:', err);
      addDebugInfo('Payment initialization error', err);
      setError('Failed to initialize payment');
    }
  };

  const initializeStripeElements = async () => {
    console.log('Initializing Stripe Elements...');
    addDebugInfo('Initializing Stripe Elements');
    try {
      const stripe = await stripePromise;
      if (!stripe) {
        throw new Error('Stripe not initialized');
      }

      const elements = stripe.elements();
      const cardElement = elements.create('card');
      cardElement.mount('#card-element');
      cardElementRef.current = cardElement;

      cardElement.on('change', ({ error }) => {
        if (error) {
          console.error('Card error:', error);
          addDebugInfo('Card error', error);
          setError(error.message);
        } else {
          setError('');
        }
      });

      console.log('Stripe Elements initialized successfully');
      addDebugInfo('Stripe Elements initialized successfully');
    } catch (err) {
      console.error('Stripe Elements initialization error:', err);
      addDebugInfo('Stripe Elements initialization error', err);
      setError('Failed to initialize Stripe Elements');
    }
  };

  const handlePayment = async () => {
    console.log('Starting payment process...');
    addDebugInfo('Starting payment process');
    
    if (!stripePromise) {
      console.error('Stripe not available');
      addDebugInfo('Stripe not available');
      setError('Stripe not available');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const stripe = await stripePromise;
      
      if (!stripe || !clientSecret || !cardElementRef.current) {
        console.error('Payment requirements not met');
        addDebugInfo('Payment requirements not met');
        setError('Payment initialization failed. Please refresh the page.');
        return;
      }

      console.log('Confirming payment...');
      addDebugInfo('Confirming payment');
      
      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElementRef.current,
          billing_details: {
            name: 'Test User'
          }
        },
        return_url: window.location.origin + '/payment-success'
      });

      if (stripeError) {
        console.error('Payment error:', stripeError);
        addDebugInfo('Payment error', stripeError);
        setError(stripeError.message || 'Payment failed. Please try again.');
      } else {
        console.log('Payment successful:', paymentIntent);
        addDebugInfo('Payment successful', paymentIntent);
        navigate(`/results/${slug}`);
      }
    } catch (err) {
      console.error('Payment process error:', err);
      addDebugInfo('Payment process error', err);
      setError('Payment failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Payment
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Stack spacing={3}>
          <TextField
            fullWidth
            label="Amount"
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            InputProps={{
              startAdornment: '$',
              endAdornment: '.00'
            }}
            disabled={loading}
          />

          <div id="card-element" style={{ width: '100%' }}>
            {/* Stripe Elements will be mounted here */}
          </div>

          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={handlePayment}
            disabled={loading || !clientSecret}
            fullWidth
          >
            {loading ? <CircularProgress size={24} /> : 'Complete Payment'}
          </Button>
        </Stack>

        <Box sx={{ mt: 4 }}>
          <Typography variant="subtitle1" gutterBottom>
            Debug Information:
          </Typography>
          {debugInfo.map((entry, index) => (
            <Typography key={index} variant="body2" sx={{ mb: 1 }}>
              {new Date(entry.timestamp).toLocaleString()} - {entry.message}
              {entry.data && <pre style={{ whiteSpace: 'pre-wrap', margin: '8px 0' }}>{JSON.stringify(entry.data, null, 2)}</pre>}
            </Typography>
          ))}
        </Box>
      </Paper>
    </Container>
  );
};

export default Payment;
