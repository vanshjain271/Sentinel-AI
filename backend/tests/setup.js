// Jest setup file
require('dotenv').config();

// Set test environment variables
process.env.NODE_ENV = 'test';
process.env.PORT = '3001'; // Use different port for tests

// Global test setup
global.console = {
  ...console,
  // Uncomment to hide console logs during tests
  // log: jest.fn(),
  // error: jest.fn(),
  // warn: jest.fn(),
};
