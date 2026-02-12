// mlService.js - SIMPLIFIED (just forwards to Flask)
const axios = require('axios');
const logger = require('../utils/logger');

class MLService {
  constructor() {
    this.flaskBaseUrl = 'http://localhost:5001';
    this.logger = logger;
  }

  async predictTraffic(features) {
    try {
      const response = await axios.post(`${this.flaskBaseUrl}/predict`, {
        features: features.slice(0, 17) // Match Flask expected features
      }, { timeout: 3000 });
      
      return response.data;
    } catch (error) {
      this.logger.error(`ML prediction failed: ${error.message}`);
      
      // Fallback
      return {
        prediction: 'normal',
        confidence: 0.5,
        threat_level: 'LOW',
        model_used: 'fallback'
      };
    }
  }

  async checkHealth() {
    try {
      const response = await axios.get(`${this.flaskBaseUrl}/health`, { timeout: 2000 });
      return response.data.ml_engine_ready || false;
    } catch {
      return false;
    }
  }
}

module.exports = MLService;