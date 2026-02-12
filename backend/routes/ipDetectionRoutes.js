// ipDetectionRoutes.js - SIMPLIFIED
const express = require('express');
const router = express.Router();

// Simple IP blocking routes
router.get('/blocked-ips', (req, res) => {
  // In production, this would query a database
  // For now, return empty or from memory
  res.json({
    success: true,
    blockedIPs: [],
    count: 0
  });
});

router.post('/block-ip', async (req, res) => {
  try {
    const { ip, reason } = req.body;
    
    if (!ip) {
      return res.status(400).json({ success: false, error: 'IP required' });
    }
    
    // Forward to Flask for SDN blocking
    const response = await require('axios').post('http://localhost:5001/block', {
      ip,
      reason: reason || 'Manual block'
    });
    
    res.json({
      success: true,
      message: `IP ${ip} blocked`,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to block IP'
    });
  }
});

module.exports = router;