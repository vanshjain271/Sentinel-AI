const axios = require('axios');

const BACKEND_URL = 'http://localhost:3000';

describe('Performance Tests', () => {
  test('Backend detection endpoint under load', async () => {
    const testTraffic = Array(1000).fill(10); // Simulate 1000 packets
    const testIP = '192.168.1.100';

    const startTime = Date.now();

    const requests = [];
    for (let i = 0; i < 20; i++) { // 20 concurrent requests
      requests.push(
        axios.post(`${BACKEND_URL}/api/detect`, {
          traffic: testTraffic,
          ip: testIP,
          packet_data: {
            packet_rate: 1000,
            avg_packet_size: 1500
          },
          network_slice: 'eMBB'
        })
      );
    }

    const responses = await Promise.all(requests);

    const endTime = Date.now();
    const duration = endTime - startTime;

    console.log(`Processed 20 concurrent detection requests in ${duration} ms`);

    // Check all responses are successful
    responses.forEach(response => {
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('prediction');
    });

    // Assert that total duration is under 5 seconds (5000 ms)
    expect(duration).toBeLessThan(5000);
  }, 60000); // 60 seconds timeout for performance test
});
