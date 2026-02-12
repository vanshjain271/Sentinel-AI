/**
 * Performance Tests for Sentinel AI Backend
 * Tests system behavior under load and concurrency
 *
 * Test Coverage:
 * - Concurrent request handling
 * - Response time measurement
 * - Throughput validation
 */

const axios = require('axios');

const BACKEND_URL = 'http://localhost:3000';
const TEST_TIMEOUT = 60000; // 60 seconds

const createDetectionPayload = (overrides = {}) => ({
  traffic: Array(1000).fill(100), // Large traffic array
  ip: '192.168.1.100',
  packet_data: {
    packet_rate: 1000,
    avg_packet_size: 1500
  },
  network_slice: 'eMBB',
  ...overrides
});

describe('Sentinel AI Backend - Performance Tests', () => {
  test('TC-PT-001: Should handle 20 concurrent detection requests within 5 seconds', async () => {
    const concurrentRequests = 20;
    const payload = createDetectionPayload();

    const startTime = Date.now();

    const requests = Array(concurrentRequests).fill().map(() =>
      axios.post(`${BACKEND_URL}/api/detect`, payload, { timeout: TEST_TIMEOUT })
    );

    const responses = await Promise.all(requests);

    const endTime = Date.now();
    const duration = endTime - startTime;

    console.log(`Processed ${concurrentRequests} concurrent detection requests in ${duration} ms`);

    // All responses should be successful
    responses.forEach(response => {
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('prediction');
    });

    // Assert total duration is under 5 seconds
    expect(duration).toBeLessThan(5000);
  }, TEST_TIMEOUT);

  test('TC-PT-002: Should maintain stable memory usage under load (manual monitoring)', async () => {
    // This test is a placeholder for manual memory monitoring during load tests
    console.log('Manual memory monitoring recommended during performance tests.');
  });
});
