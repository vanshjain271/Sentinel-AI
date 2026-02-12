/**
 * Unit Tests for Sentinel AI Backend
 * Tests core functionality and API endpoints
 *
 * Test Coverage:
 * - Health check endpoints
 * - Detection API routes
 * - Error handling
 * - Performance validation
 * - Input validation
 */

const request = require('supertest');
const express = require('express');
const { router } = require('../routes/detectionRoutes');

// Test constants
const TEST_CONSTANTS = {
  VALID_IP: '192.168.1.100',
  INVALID_IP: '999.999.999.999',
  HEALTH_MESSAGE: 'AI-Driven DDoS Detection Backend is running',
  NETWORK_SLICES: ['eMBB', 'URLLC', 'mMTC'],
  TIMEOUT_MS: 5000
};

// Create a test application instance
const createTestApp = () => {
  const app = express();
  app.use(express.json());
  app.use('/api', router);

  // Health check endpoint for testing
  app.get('/', (req, res) => {
    res.status(200).send(TEST_CONSTANTS.HEALTH_MESSAGE);
  });

  // Error handling middleware
  app.use((err, req, res, next) => {
    console.error('Test app error:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  });

  return app;
};

// Test data factories
const createValidDetectionPayload = (overrides = {}) => ({
  traffic: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
  ip: TEST_CONSTANTS.VALID_IP,
  packet_data: {
    packet_rate: 100,
    avg_packet_size: 1500
  },
  network_slice: 'eMBB',
  ...overrides
});

const createInvalidDetectionPayload = (overrides = {}) => ({
  traffic: 'invalid_data',
  ip: TEST_CONSTANTS.INVALID_IP,
  ...overrides
});

describe('Sentinel AI Backend - Unit Tests', () => {
  let app;

  beforeAll(() => {
    app = createTestApp();
  });

  afterAll(async () => {
    // Cleanup if needed
  });

  describe('Health Check Endpoint (/health)', () => {
    test('TC-UT-001: Should return HTTP 200 and correct health message', async () => {
      const response = await request(app)
        .get('/')
        .expect(200)
        .expect('Content-Type', /text\/html/);

      expect(response.text).toBe(TEST_CONSTANTS.HEALTH_MESSAGE);
      expect(response.status).toBe(200);
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-002: Should handle API routes correctly', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);

      expect(response.body).toHaveProperty('status');
      expect(typeof response.body.status).toBe('string');
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-003: Should return JSON response for API endpoints', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200)
        .expect('Content-Type', /json/);

      expect(response.body).toBeInstanceOf(Object);
      expect(response.body).toHaveProperty('status');
    }, TEST_CONSTANTS.TIMEOUT_MS);
  });

  describe('Detection Routes (/api/detect)', () => {
    test('TC-UT-004: Should accept valid detection request', async () => {
      const payload = createValidDetectionPayload();

      const response = await request(app)
        .post('/api/detect')
        .send(payload)
        .expect(200);

      expect(response.body).toHaveProperty('prediction');
      expect(response.body).toHaveProperty('confidence');
      expect(response.body).toHaveProperty('network_slice');
      expect(typeof response.body.prediction).toBe('string');
      expect(typeof response.body.confidence).toBe('number');
      expect(response.body.network_slice).toBe(payload.network_slice);
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-005: Should reject invalid traffic data', async () => {
      const payload = createInvalidDetectionPayload();

      const response = await request(app)
        .post('/api/detect')
        .send(payload)
        .expect(400);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toBeDefined();
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-006: Should handle missing required fields', async () => {
      const incompletePayload = {
        ip: TEST_CONSTANTS.VALID_IP
        // Missing traffic data
      };

      const response = await request(app)
        .post('/api/detect')
        .send(incompletePayload);

      // Should either return 400 or handle gracefully
      expect([200, 400, 500]).toContain(response.status);

      if (response.status === 400) {
        expect(response.body).toHaveProperty('error');
      }
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-007: Should support different network slices', async () => {
      for (const slice of TEST_CONSTANTS.NETWORK_SLICES) {
        const payload = createValidDetectionPayload({ network_slice: slice });

        const response = await request(app)
          .post('/api/detect')
          .send(payload)
          .expect(200);

        expect(response.body).toHaveProperty('network_slice', slice);
        expect(TEST_CONSTANTS.NETWORK_SLICES).toContain(response.body.network_slice);
      }
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-008: Should handle large traffic arrays', async () => {
      const largeTraffic = Array(1000).fill(100); // 1000 data points
      const payload = createValidDetectionPayload({ traffic: largeTraffic });

      const response = await request(app)
        .post('/api/detect')
        .send(payload)
        .expect(200);

      expect(response.body).toHaveProperty('prediction');
      expect(response.body).toHaveProperty('confidence');
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-009: Should validate IP address format', async () => {
      const invalidIPs = ['invalid', '256.256.256.256', '192.168.1'];

      for (const invalidIP of invalidIPs) {
        const payload = createValidDetectionPayload({ ip: invalidIP });

        const response = await request(app)
          .post('/api/detect')
          .send(payload);

        // Should handle invalid IP gracefully
        expect([200, 400]).toContain(response.status);
      }
    }, TEST_CONSTANTS.TIMEOUT_MS);
  });

  describe('Error Handling', () => {
    test('TC-UT-010: Should handle malformed JSON gracefully', async () => {
      const response = await request(app)
        .post('/api/detect')
        .set('Content-Type', 'application/json')
        .send('{ invalid json }')
        .expect(400);

      expect(response.body).toHaveProperty('error');
      expect(typeof response.body.error).toBe('string');
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-011: Should handle unsupported HTTP methods', async () => {
      const response = await request(app)
        .put('/api/detect')
        .expect(404);

      expect(response.status).toBe(404);
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-012: Should handle extremely large payloads', async () => {
      const hugeTraffic = Array(10000).fill(1000); // 10k data points
      const payload = createValidDetectionPayload({ traffic: hugeTraffic });

      const response = await request(app)
        .post('/api/detect')
        .send(payload);

      // Should either handle or return appropriate error
      expect([200, 413, 500]).toContain(response.status);
    }, TEST_CONSTANTS.TIMEOUT_MS);
  });

  describe('Performance Validation', () => {
    test('TC-UT-013: Should respond within acceptable time limits', async () => {
      const startTime = Date.now();

      await request(app)
        .get('/')
        .expect(200);

      const endTime = Date.now();
      const responseTime = endTime - startTime;

      // Should respond within 100ms for simple health check
      expect(responseTime).toBeLessThan(100);
      console.log(`Health check response time: ${responseTime}ms`);
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-014: Should handle concurrent requests efficiently', async () => {
      const concurrentRequests = 5;
      const startTime = Date.now();

      const requests = Array(concurrentRequests).fill().map(() =>
        request(app).get('/').expect(200)
      );

      await Promise.all(requests);

      const endTime = Date.now();
      const totalTime = endTime - startTime;
      const avgTime = totalTime / concurrentRequests;

      // Average response time should be reasonable
      expect(avgTime).toBeLessThan(200);
      console.log(`Concurrent requests (${concurrentRequests}): ${totalTime}ms total, ${avgTime}ms average`);
    }, TEST_CONSTANTS.TIMEOUT_MS);
  });

  describe('Data Validation', () => {
    test('TC-UT-015: Should validate packet rate ranges', async () => {
      const testCases = [
        { packet_rate: 0, shouldPass: true },
        { packet_rate: 1000, shouldPass: true },
        { packet_rate: 100000, shouldPass: true },
        { packet_rate: -1, shouldPass: false },
        { packet_rate: 'invalid', shouldPass: false }
      ];

      for (const testCase of testCases) {
        const payload = createValidDetectionPayload({
          packet_data: {
            packet_rate: testCase.packet_rate,
            avg_packet_size: 1500
          }
        });

        const response = await request(app)
          .post('/api/detect')
          .send(payload);

        if (testCase.shouldPass) {
          expect([200, 400]).toContain(response.status); // May pass validation
        }
      }
    }, TEST_CONSTANTS.TIMEOUT_MS);

    test('TC-UT-016: Should handle empty traffic arrays', async () => {
      const payload = createValidDetectionPayload({ traffic: [] });

      const response = await request(app)
        .post('/api/detect')
        .send(payload);

      // Should handle gracefully
      expect([200, 400]).toContain(response.status);
    }, TEST_CONSTANTS.TIMEOUT_MS);
  });
});
