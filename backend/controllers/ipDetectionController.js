// ipDetectionController.js
const axios = require('axios');
const { ML_MODEL_URL, ABUSEIPDB_API_KEY, RYU_URL } = process.env;

// Track IP behavior
const ipBehavior = new Map();
const IP_BEHAVIOR_TTL = 3600000; // 1 hour

// ML model client
const mlClient = axios.create({
  baseURL: ML_MODEL_URL?.replace('/predict', '') || 'http://localhost:5001',
  timeout: 2000,
  headers: { 'Content-Type': 'application/json' }
});

// Ryu Controller URL (same as in app.py)
const ryuBaseUrl = RYU_URL || 'http://192.168.56.101:8080';

// Update IP behavior with new request data
function updateIpBehavior(ip, requestData) {
  const now = Date.now();
  const behavior = ipBehavior.get(ip) || {
    firstSeen: now,
    lastSeen: now,
    requestCount: 0,
    suspiciousCount: 0,
    lastRequest: null,
    isBlocked: false
  };

  behavior.requestCount++;
  behavior.lastSeen = now;
  behavior.lastRequest = requestData;

  // Clean up old entries
  for (const [addr, data] of ipBehavior.entries()) {
    if (now - data.lastSeen > IP_BEHAVIOR_TTL) {
      ipBehavior.delete(addr);
    }
  }

  ipBehavior.set(ip, behavior);
  return behavior;
}

// Check if IP should be blocked
function shouldBlockIP(ip, detectionResult) {
  const behavior = ipBehavior.get(ip);
  if (!behavior) return false;

  // If already blocked, keep it blocked
  if (behavior.isBlocked) return true;

  // Check detection result
  if (detectionResult.prediction === 'ddos' || detectionResult.isDDoS) {
    behavior.suspiciousCount++;

    // Block if multiple suspicious activities detected
    if (behavior.suspiciousCount >= 3) {
      behavior.isBlocked = true;
      return true;
    }
  }

  // Check request rate (more than 100 requests per minute)
  const requestRate =
    (behavior.requestCount /
      ((behavior.lastSeen - behavior.firstSeen) / 60000)) || 0;
  if (requestRate > 100) {
    behavior.isBlocked = true;
    return true;
  }

  return false;
}

// Block IP in the network via Ryu SDN controller
async function blockIP(ip, reason, isSimulated = false) {
  console.log(
    `Blocking IP ${ip}: ${reason} ${isSimulated ? '[SIMULATED]' : ''}`
  );

  // Update local behavior map
  const behavior = ipBehavior.get(ip) || {};
  behavior.isBlocked = true;
  behavior.blockedAt = new Date().toISOString();
  behavior.blockReason = reason;
  ipBehavior.set(ip, behavior);

  // Construct SDN DROP rule (same as Python block_ip in app.py)
  const rule = {
    dpid: '0000000000000001',
    priority: 60000,
    match: { ipv4_src: ip },
    actions: []
  };

  try {
    const url = `${ryuBaseUrl}/stats/flowentry/add`;
    const resp = await axios.post(url, rule, { timeout: 3000 });
    if (resp.status >= 200 && resp.status < 300) {
      console.log(`Ryu SDN rule installed for ${ip}`);
      return true;
    }
    console.error(
      `Ryu responded with status ${resp.status} while blocking ${ip}`
    );
  } catch (err) {
    console.error(`Failed to contact Ryu controller for ${ip}:`, err.message);
  }

  // Even if Ryu call fails, we consider it logically blocked in behavior map
  return false;
}

// Main detection function
const detectAndMitigate = async (req, res, next) => {
  try {
    const ip = req.ip || req.connection.remoteAddress;
    const { traffic, packet_data, network_slice } = req.body;

    // Update IP behavior
    updateIpBehavior(ip, {
      timestamp: new Date().toISOString(),
      userAgent: req.headers['user-agent'],
      endpoint: req.originalUrl,
      method: req.method
    });

    // Get detection result from ML model
    const mlResponse = await mlClient.post('/predict', {
      traffic,
      ip_address: ip,
      packet_data: packet_data || {},
      network_slice: network_slice || 'eMBB'
    });

    const detectionResult = mlResponse.data;

    // Check if IP should be blocked
    if (shouldBlockIP(ip, detectionResult)) {
      // Trigger mitigation via Ryu
      await blockIP(ip, 'Suspicious activity detected', false);

      // Emit event for real-time updates
      const io = req.app.get('io');
      if (io) {
        io.emit('ip_blocked', {
          ip,
          timestamp: new Date().toISOString(),
          reason: 'Suspicious activity detected',
          detectionResult,
          threatLevel: 'high',
          mitigation: 'SDN DROP Rule',
          isSimulated: false
        });
      }

      return res.status(429).json({
        success: false,
        error: 'Access denied',
        message: 'Your IP has been blocked due to suspicious activity',
        blocked: true
      });
    }

    // If not blocked, return detection result
    res.json({
      success: true,
      ...detectionResult,
      ip,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('IP Detection Error:', error);
    next(error);
  }
};

module.exports = {
  detectAndMitigate,
  blockIP,
  // For testing
  _ipBehavior: ipBehavior
};
