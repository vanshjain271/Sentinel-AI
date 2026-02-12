const axios = require('axios');

const BACKEND_URL = 'http://localhost:3000';
const ML_URL = 'http://localhost:5001';

describe('Integration Tests', () => {
  describe('End-to-End Detection Flow', () => {
    test('should complete full detection cycle', async () => {
      // Test data
      const testTraffic = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
      const testIP = '192.168.1.100';

      try {
        // Step 1: Test backend health
        console.log('Step 1: Testing backend health...');
        const backendHealth = await axios.get(`${BACKEND_URL}/`);
        expect(backendHealth.status).toBe(200);
        expect(backendHealth.data).toContain('running');
        console.log('✅ Backend is healthy');

        // Step 2: Test ML service health
        console.log('Step 2: Testing ML service health...');
        const mlHealth = await axios.get(`${ML_URL}/`);
        expect(mlHealth.status).toBe(200);
        expect(mlHealth.data.status).toBe('running');
        console.log('✅ ML service is healthy');

        // Step 3: Test ML prediction directly
        console.log('Step 3: Testing ML prediction...');
        const mlResponse = await axios.post(`${ML_URL}/predict`, {
          traffic: testTraffic,
          ip_address: testIP,
          packet_data: {
            packet_rate: 100,
            avg_packet_size: 1500
          },
          network_slice: 'eMBB'
        });
        expect(mlResponse.status).toBe(200);
        expect(mlResponse.data).toHaveProperty('prediction');
        expect(mlResponse.data).toHaveProperty('confidence');
        console.log('✅ ML prediction successful:', mlResponse.data.prediction);

        // Step 4: Test backend detection endpoint
        console.log('Step 4: Testing backend detection endpoint...');
        const backendResponse = await axios.post(`${BACKEND_URL}/api/detect`, {
          traffic: testTraffic,
          ip: testIP,
          packet_data: {
            packet_rate: 100,
            avg_packet_size: 1500
          },
          network_slice: 'eMBB'
        });
        expect(backendResponse.status).toBe(200);
        expect(backendResponse.data).toHaveProperty('prediction');
        console.log('✅ Backend detection successful');

        // Step 5: Verify results consistency
        console.log('Step 5: Verifying results consistency...');
        expect(backendResponse.data.prediction).toBeDefined();
        expect(typeof backendResponse.data.confidence).toBe('number');
        console.log('✅ Results are consistent');

        console.log('🎉 All integration tests passed!');

      } catch (error) {
        console.error('❌ Integration test failed:', error.message);
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
        }
        throw error;
      }
    }, 30000); // 30 second timeout for integration tests

    test('should handle service unavailability gracefully', async () => {
      try {
        // Try to connect to a non-existent service
        await axios.get('http://localhost:9999/', { timeout: 5000 });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.code).toBe('ECONNREFUSED');
        console.log('✅ Gracefully handles service unavailability');
      }
    });
  });
});
