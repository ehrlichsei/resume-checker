import '@testing-library/jest-dom';
import '@testing-library/jest-dom/extend-expect';

// Mock Stripe
jest.mock('@stripe/stripe-js', () => ({
  loadStripe: jest.fn(() => ({
    elements: jest.fn(() => ({
      create: jest.fn(() => ({
        mount: jest.fn()
      }))
    })),
    confirmCardPayment: jest.fn()
  }))
}));

// Mock fetch
global.fetch = jest.fn(() => Promise.resolve({
  json: () => Promise.resolve({
    client_secret: 'test_secret_123',
    payment_intent_id: 'pi_123'
  })
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock
});

// Mock matchMedia
window.matchMedia = jest.fn().mockImplementation(query => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: jest.fn(), // deprecated
  removeListener: jest.fn(), // deprecated
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn()
}));

// Mock window.confirm
window.confirm = jest.fn(() => true);

// Mock IntersectionObserver
window.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn()
}));

// Mock ResizeObserver
window.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn()
}));

// Mock document
Object.defineProperty(document, 'body', {
  value: {
    clientWidth: 1920,
    clientHeight: 1080
  }
});

// Mock Element
Object.defineProperty(Element.prototype, 'getBoundingClientRect', {
  value: jest.fn(() => ({
    width: 100,
    height: 100,
    top: 0,
    left: 0,
    bottom: 100,
    right: 100
  }))
});

// Mock HTMLMediaElement
Object.defineProperty(HTMLMediaElement.prototype, 'play', {
  value: jest.fn()
});

// Mock HTMLCanvasElement
Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
  value: jest.fn()
});

// Mock window.scrollTo
window.scrollTo = jest.fn();
