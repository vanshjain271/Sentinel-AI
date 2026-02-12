// detectionController.js
const axios = require('axios');
require('dotenv').config();

// Optimized axios instances with connection pooling
const mlClient = axios.create({
  baseURL: process.env.ML_MODEL_URL?.replace('/predict', '') || 'http://localhost:5001',
  timeout: 600,
  headers: { 'Content-Type': 'application/json', 'Connection': 'keep-alive' },
  httpAgent: new (require('http').Agent)({ keepAlive: true, maxSockets: 5 })
});

const abuseClient = axios.create({
  baseURL: process.env.ABUSEIPDB_URL?.replace('/check', '') || 'https://api.abuseipdb.com/api/v2',
  timeout: 400,
  headers: { 
    'Key': process.env.ABUSEIPDB_API_KEY,
    'Accept': 'application/json',
    'Connection': 'keep-alive'
  },
  httpsAgent: new (require('https').Agent)({ keepAlive: true, maxSockets: 3 })
});

// IP cache to avoid repeated AbuseIPDB calls
const ipCache = new Map();
const IP_CACHE_TTL = 300000;

const detectDDoS = async (req, res) => {
  try {
    const { traffic, ip, packet_data, network_slice } = req.body;

    // Forward to Flask ML engine
    const response = await axios.post('http://localhost:5001/predict', {
      features: traffic.slice(0, 17) // Use compatible feature count
    }, { timeout: 3000 });

    res.json({
      prediction: response.data.prediction || 'normal',
      confidence: response.data.confidence || 0.5,
      explanation: response.data.explanation,
      model_used: 'enhanced_flask',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Detection error:', error.message);
    // Fallback
    res.json({
      prediction: 'normal',
      confidence: 0.5,
      explanation: null,
      model_used: 'fallback',
      error: 'ML service unavailable'
    });
  }
};

module.exports = { detectDDoS };