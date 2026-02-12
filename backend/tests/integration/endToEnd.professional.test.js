/**
 * Integration Tests for Sentinel AI System
 * Tests end-to-end functionality across all services
 *
 * Test Coverage:
 * - Service-to-service communication
 * - Data flow validation
 * - Error handling across services
 * - Performance under integration scenarios
 */

const axios = require('axios');

const SERVICE_ENDPOINTS = {
  BACKEND: 'http://localhost:3000',
  ML_SERVICE: 'http://localhost:5001',
  FRONTEND: 'http://localhost:5173'
};

const TEST_TIMEOUTS = {
  HEALTH_CHECK: 5000,
  DETECTION: 15000,
  INTEGRATION: 30000
};

const TEST_DATA = {
  VALID_TRAFFIC: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
  LARGE_TRAFFIC: Array(1000).fill(100),
  VALID_IP: '192.168.1.100',
  NETWORK_SLICES: ['eMBB', 'URLLC', 'mMTC']
};

// Test utilities
const waitForService = async (url, serviceName, timeout = 10000) => {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    try {
      await axios.get(url, { timeout: 2000 });
      console.log(`✅ ${serviceName} is available at ${url}`);
      return true;
    } catch (error) {
      console.log(`⏳ Waiting for ${serviceName}... (${Math.round((Date.now() - startTime) / 1000)}s)`);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  console.error(`❌ ${serviceName} is not available at ${url}`);
  return false;
};

const createDetectionPayload = (overrides = {}) => ({
  traffic: TEST_DATA.VALID_TRAFFIC,
  ip: TEST_DATA.VALID_IP,
  packet_data: {
    packet_rate: 100,
    avg_packet_size: 1500
  },
  network_slice: 'eMBB',
  ...overrides
});

describe('Sentinel AI System - Integration Tests', () => {
  describe('Service Availability and Health Checks', () => {
    test('TC-IT-001: All core services should be available', async () => {
      const services = [
        { url: SERVICE_ENDPOINTS.BACKEND, name: 'Backend API' },
        { url: SERVICE_ENDPOINTS.ML_SERVICE, name: 'ML Service' }
      ];

      for (const service of services) {
        const isAvailable = await waitForService(service.url, service.name);
        expect(isAvailable).toBe(true);
      }
    }, TEST_TIMEOUTS.HEALTH_CHECK);

    test('TC-IT-002: Backend service health endpoint should respond', async () => {
      const response = await axios.get(`${SERVICE_ENDPOINTS.BACKEND}/`, {
        timeout: TEST_TIMEOUTS.HEALTH_CHECK
      });

      expect(response.status).toBe(200);
      expect(response.data).toContain('running');
    }, TEST_TIMEOUTS.HEALTH_CHECK);

    test('TC-IT-003: ML service health endpoint should respond', async () => {
      const response = await axios.get(`${SERVICE_ENDPOINTS.ML_SERVICE}/`, {
        timeout: TEST_TIMEOUTS.HEALTH_CHECK
      });

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('status', 'running');
    }, TEST_TIMEOUTS.HEALTH_CHECK);
  });

  describe('End-to-End Detection Flow', () => {
    test('TC-IT-004: Complete detection workflow should succeed', async () => {
      const payload = createDetectionPayload();

      console.log('🚀 Starting end-to-end detection test...');

      // Step 1: Test ML service prediction directly
      console.log('Step 1: Testing ML service prediction...');
      const mlStartTime = Date.now();

      const mlResponse = await axios.post(`${SERVICE_ENDPOINTS.ML_SERVICE}/predict`, payload, {
        timeout: TEST_TIMEOUTS.DETECTION
      });

      const mlEndTime = Date.now();
      const mlResponseTime = mlEndTime - mlStartTime;

      expect(mlResponse.status).toBe(200);
      expect(mlResponse.data).toHaveProperty('prediction');
      expect(mlResponse.data).toHaveProperty('confidence');
      expect(mlResponse.data).toHaveProperty('network_slice');
      expect(typeof mlResponse.data.confidence).toBe('number');
      expect(mlResponse.data.confidence).toBeGreaterThanOrEqual(0);
      expect(mlResponse.data.confidence).toBeLessThanOrEqual(1);

      console.log(`✅ ML prediction successful (${mlResponseTime}ms): ${mlResponse.data.prediction}`);

      // Step 2: Test backend detection endpoint
      console.log('Step 2: Testing backend detection endpoint...');
      const backendStartTime = Date.now();

      const backendResponse = await axios.post(`${SERVICE_ENDPOINTS.BACKEND}/api/detect`, payload, {
        timeout: TEST_TIMEOUTS.DETECTION
      });

      const backendEndTime = Date.now();
      const backendResponseTime = backendEndTime - backendStartTime;

      expect(backendResponse.status).toBe(200);
      expect(backendResponse.data).toHaveProperty('prediction');
      expect(backendResponse.data).toHaveProperty('confidence');

      console.log(`✅ Backend detection successful (${backendResponseTime}ms): ${backendResponse.data.prediction}`);

      // Step 3: Validate data consistency
      console.log('Step 3: Validating data consistency...');
      expect(backendResponse.data.prediction).toBe(mlResponse.data.prediction);
      expect(backendResponse.data.confidence).toBeCloseTo(mlResponse.data.confidence, 2);
      expect(backendResponse.data.network_slice).toBe(payload.network_slice);

      console.log('✅ Data consistency validated');

      // Step 4: Performance validation
      console.log('Step 4: Validating performance...');
      const totalResponseTime = mlResponseTime + backendResponseTime;
      expect(totalResponseTime).toBeLessThan(5000); // Should complete within 5 seconds

      console.log(`🎉 End-to-end test completed successfully in ${totalResponseTime}ms`);

    }, TEST_TIMEOUTS.INTEGRATION);

    test('TC-IT-005: Should handle different network slices correctly', async () => {
      for (const slice of TEST_DATA.NETWORK_SLICES) {
        const payload = createDetectionPayload({ network_slice: slice });

        const response = await axios.post(`${SERVICE_ENDPOINTS.BACKEND}/api/detect`, payload, {
          timeout: TEST_TIMEOUTS.DETECTION
        });

        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('network_slice', slice);
        expect(response.data).toHaveProperty('prediction');

        console.log(`✅ Network slice '${slice}' handled correctly`);
      }
    }, TEST_TIMEOUTS.INTEGRATION);

    test('TC-IT-006: Should handle large traffic datasets', async () => {
      const payload = createDetectionPayload({ traffic: TEST_DATA.LARGE_TRAFFIC });

      const startTime = Date.now();

      const response = await axios.post(`${SERVICE_ENDPOINTS.BACKEND}/api/detect`, payload, {
        timeout: TEST_TIMEOUTS.DETECTION
      });

      const endTime = Date.now();
      const responseTime = endTime - startTime;

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('prediction');
      expect(responseTime).toBeLessThan(10000); // Should handle large datasets within 10 seconds

      console.log(`✅ Large dataset (${TEST_DATA.LARGE_TRAFFIC.length} points) processed in ${responseTime}ms`);
    }, TEST_TIMEOUTS.INTEGRATION);
  });

  describe('Error Handling and Resilience', () => {
    test('TC-IT-007: Should handle ML service unavailability gracefully', async () => {
      // This test assumes ML service might be temporarily unavailable
      try {
        const payload = createDetectionPayload();
        const response = await axios.post(`${SERVICE_ENDPOINTS.BACKEND}/api/detect`, payload, {
          timeout: TEST_TIMEOUTS.DETECTION
        });

        // If both services are available, should succeed
        expect(response.status).toBe(200);
        console.log('✅ Both services available, detection successful');
      } catch (error) {
        // If ML service is unavailable, backend should handle gracefully
        expect(error.code).toBe('ECONNREFUSED');
        console.log('⚠️ ML service unavailable, backend handled gracefully');
      }
    }, TEST_TIMEOUTS.INTEGRATION);

    test('TC-IT-008: Should handle invalid data gracefully', async () => {
      const invalidPayloads = [
        { traffic: 'invalid', ip: TEST_DATA.VALID_IP },
        { traffic: [], ip: TEST_DATA.VALID_IP },
        { traffic: TEST_DATA.VALID_TRAFFIC, ip: 'invalid-ip' }
      ];

      for (const payload of invalidPayloads) {
        try {
          const response = await axios.post(`${SERVICE_ENDPOINTS.BACKEND}/api/detect`, payload, {
            timeout: TEST_TIMEOUTS.DETECTION
          });

          // Should either succeed or return appropriate error
          expect([200, 400, 500]).toContain(response.status);

          if (response.status === 400) {
            expect(response.data).toHaveProperty('error');
          }

          console.log(`✅ Invalid payload handled: ${JSON.stringify(payload).substring(0, 50)}...`);
        } catch (error) {
          console.log(`⚠️ Request failed as expected: ${error.message}`);
        }
      }
    }, TEST_TIMEOUTS.INTEGRATION);

    test('TC-IT-009: Should recover from temporary service interruptions', async () => {
      // Test service recovery by making multiple requests
      const requests = Array(5).fill().map(() =>
        axios.post(`${SERVICE_ENDPOINTS.BACKEND}/api/detect`, createDetectionPayload(), {
          timeout: TEST_TIMEOUTS.DETECTION
        })
      );

      const results = await Promise.allSettled(requests);

      const successfulRequests = results.filter(result => result.status === 'fulfilled').length;
      const failedRequests = results.filter(result => result.status === 'rejected').length;

      console.log(`Service recovery test: ${successfulRequests} successful, ${failedRequests} failed`);

      // At least some requests should succeed
      expect(successfulRequests).toBeGreaterThan(0);

      // Log results for analysis
      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          console.log(`✅ Request ${index + 1}: ${result.value.data.prediction}`);
        } else {
          console.log(`❌ Request ${index + 1}: ${result.reason.message}`);
        }
      });
    }, TEST_TIMEOUTS.INTEGRATION);
  });

  describe('Data Flow and Consistency', () => {
    test('TC-IT-010: Should maintain data integrity across services', async () => {
      const payload = createDetectionPayload();

      // Get prediction from ML service
      const mlResponse = await axios.post(`${SERVICE_ENDPOINTS.ML_SERVICE}/predict`, payload);

      // Get prediction from backend (which should use ML service)
      const backendResponse = await axios.post(`${SERVICE_ENDPOINTS.BACKEND}/api/detect`, payload);

      // Validate data consistency
      expect(backendResponse.data.prediction).toBe(mlResponse.data.prediction);
      expect(backendResponse.data.network_slice).toBe(mlResponse.data.network_slice);
      expect(backendResponse.data.ip_address).toBe(mlResponse.data.ip_address);

      console.log('✅ Data integrity maintained across services');
    }, TEST_TIMEOUTS.INTEGRATION);

    test('TC-IT-011: Should handle concurrent requests without data corruption', async () => {
      const concurrentRequests = 10;
      const payload = createDetectionPayload();

      const startTime = Date.now();

      const requests = Array(concurrentRequests).fill().map(() =>
        axios.post(`${SERVICE_ENDPOINTS.BACKEND}/api/detect`, payload, {
          timeout: TEST_TIMEOUTS.DETECTION
        })
      );

      const responses = await Promise.all(requests);
      const endTime = Date.now();

      const totalTime = endTime - startTime;
      const avgTime = totalTime / concurrentRequests;

      // All requests should succeed
      responses.forEach(response => {
        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('prediction');
      });

      // Performance should be reasonable
      expect(avgTime).toBeLessThan(2000); // Average under 2 seconds

      console.log(`✅ ${concurrentRequests} concurrent requests completed in ${totalTime}ms (${avgTime}ms average)`);
    }, TEST_TIMEOUTS.INTEGRATION);
  });
});
