// abuseIPDBService.js
const axios = require('axios');

const checkIP = async (ip) => {
  try {
    const response = await axios.get(process.env.ABUSEIPDB_URL, {
      params: { ipAddress: ip, maxAgeInDays: 90 },
      headers: {
        Key: process.env.ABUSEIPDB_API_KEY,
        Accept: 'application/json'
      }
    });
    return response.data.data; // Returns { abuseConfidenceScore, ... }
  } catch (err) {
    throw new Error(`AbuseIPDB error: ${err.message}`);
  }
};

module.exports = { checkIP };