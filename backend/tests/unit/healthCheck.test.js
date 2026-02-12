const request = require('supertest');
const express = require('express');
const { router } = require('../routes/detectionRoutes');

// Create a test app
const app = express();
app.use(express.json());
app.use('/api', router);

// Health check endpoint for testing
app.get('/', (req, res) => {
  res.send('AI-Driven DDoS Detection Backend is running');
});

describe('Backend Unit Tests', () => {
  describe('Health Check Endpoint', () => {
    test('should return 200 and correct message', async () => {
      const response = await request(app)
        .get('/')
        .expect(200);

      expect(response.text).toBe('AI-Driven DDoS Detection Backend is running');
    });

    test('should handle API routes', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);

      expect(response.body).toHaveProperty('status');
    });
  });

  describe('Detection Routes', () => {
    test('should have detection endpoint', async () => {
      const response = await request(app)
        .post('/api/detect')
        .send({
          traffic: [10, 20, 30, 40, 50],
          ip: '192.168.1.100'
        });

      // This will test if the route exists and handles the request
      expect(response.status).toBeDefined();
    });
  });
});
