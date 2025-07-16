import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import Payment from '../Payment';
import { loadStripe } from '@stripe/stripe-js';

// Mock Stripe
jest.mock('@stripe/stripe-js');

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock navigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => ({ resumeId: '1' }),
}));

describe('Payment Component', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockNavigate.mockClear();
  });

  test('renders payment form correctly', () => {
    render(
      <MemoryRouter initialEntries={['/payment/1']}>
        <Routes>
          <Route path="/payment/:resumeId" element={<Payment />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Payment')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /complete payment/i })).toBeInTheDocument();
    expect(screen.getByTestId('card-element')).toBeInTheDocument();
  });

  test('handles successful payment intent creation', async () => {
    mockFetch.mockResolvedValueOnce({
      json: () => Promise.resolve({
        client_secret: 'test_secret_123',
        payment_intent_id: 'pi_123'
      })
    });

    render(
      <MemoryRouter initialEntries={['/payment/1']}>
        <Routes>
          <Route path="/payment/:resumeId" element={<Payment />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/payment/create',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
      );
    });
  });

  test('handles Stripe Elements initialization', async () => {
    const mockStripe = {
      elements: () => ({
        create: () => ({
          mount: jest.fn()
        })
      })
    };
    loadStripe.mockResolvedValue(mockStripe);

    mockFetch.mockResolvedValueOnce({
      json: () => Promise.resolve({
        client_secret: 'test_secret_123',
        payment_intent_id: 'pi_123'
      })
    });

    render(
      <MemoryRouter initialEntries={['/payment/1']}>
        <Routes>
          <Route path="/payment/:resumeId" element={<Payment />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(loadStripe).toHaveBeenCalled();
      expect(screen.getByTestId('card-element')).toBeInTheDocument();
    });
  });

  test('handles payment error', async () => {
    mockFetch.mockResolvedValueOnce({
      json: () => Promise.resolve({
        client_secret: 'test_secret_123',
        payment_intent_id: 'pi_123'
      })
    });

    const { getByText } = render(
      <MemoryRouter initialEntries={['/payment/1']}>
        <Routes>
          <Route path="/payment/:resumeId" element={<Payment />} />
        </Routes>
      </MemoryRouter>
    );

    const errorButton = getByText(/complete payment/i);
    fireEvent.click(errorButton);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });

  test('navigates to results on successful payment', async () => {
    mockFetch.mockResolvedValueOnce({
      json: () => Promise.resolve({
        client_secret: 'test_secret_123',
        payment_intent_id: 'pi_123'
      })
    }).mockResolvedValueOnce({
      json: () => Promise.resolve({
        success: true,
        payment_status: 'succeeded'
      })
    });

    const mockStripe = {
      confirmCardPayment: jest.fn().mockResolvedValue({
        error: null,
        paymentIntent: {
          id: 'pi_123',
          payment_method: 'pm_123'
        }
      })
    };
    loadStripe.mockResolvedValue(mockStripe);

    render(
      <MemoryRouter initialEntries={['/payment/1']}>
        <Routes>
          <Route path="/payment/:resumeId" element={<Payment />} />
        </Routes>
      </MemoryRouter>
    );

    const paymentButton = screen.getByText(/complete payment/i);
    fireEvent.click(paymentButton);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/results/1');
    });
  });

  test('displays debug information', async () => {
    mockFetch.mockResolvedValueOnce({
      json: () => Promise.resolve({
        client_secret: 'test_secret_123',
        payment_intent_id: 'pi_123'
      })
    });

    render(
      <MemoryRouter initialEntries={['/payment/1']}>
        <Routes>
          <Route path="/payment/:resumeId" element={<Payment />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/debug information/i)).toBeInTheDocument();
      expect(screen.getByText(/payment component mounted/i)).toBeInTheDocument();
    });
  });
});
