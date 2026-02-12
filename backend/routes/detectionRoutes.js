// detectionRoutes.js - SIMPLIFIED
const express = require('express');
const os = require('os');
const { detectDDoS } = require('../controllers/detectionController');

const router = express.Router();

// Get local IPs (unchanged)
router.get('/local-ips', (req, res) => {
  try {
    const interfaces = os.networkInterfaces();
    const results = [];
    
    for (const [name, nets] of Object.entries(interfaces)) {
      const nameL = name.toLowerCase();
      const isVirtual = nameL.includes('vmware') || nameL.includes('virtualbox');
      
      if (isVirtual) continue;
      
      const isEthernet = nameL.includes('ethernet') && !nameL.includes('vmware');
      const isWiFi = nameL.includes('wi-fi') || nameL.includes('wifi');
      
      if (isEthernet || isWiFi) {
        for (const net of nets) {
          if (net.family === 'IPv4' && !net.internal) {
            results.push({ 
              interface: name, 
              address: net.address,
              type: isEthernet ? 'Ethernet' : 'Wi-Fi'
            });
          }
        }
      }
    }
    
    res.json(results);
  } catch (error) {
    console.error('Error getting local IPs:', error);
    res.status(500).json({ error: 'Failed to get local IPs' });
  }
});

// Start capture - forward to Flask
router.post('/start-capture', async (req, res) => {
  try {
    const { targetIP, interfaceName } = req.body;
    
    if (!targetIP) {
      return res.status(400).json({ error: 'targetIP required' });
    }
    
    // Forward to Flask
    const response = await require('axios').post('http://localhost:5001/start-capture', {
      targetIP,
      interface: interfaceName || 'Wi-Fi'
    });
    
    res.json({ success: true, message: 'Capture started via Flask' });
  } catch (error) {
    console.error('Error starting capture:', error);
    res.status(500).json({ error: 'Failed to start capture' });
  }
});

// Stop capture - forward to Flask
router.post('/stop-capture', async (req, res) => {
  try {
    await require('axios').post('http://localhost:5001/stop-capture');
    res.json({ success: true, message: 'Capture stopped' });
  } catch (error) {
    console.error('Error stopping capture:', error);
    res.status(500).json({ error: 'Failed to stop capture' });
  }
});

// Capture status
router.get('/capture-status', async (req, res) => {
  try {
    const response = await require('axios').get('http://localhost:5001/health');
    res.json({
      isCapturing: response.data.capturing || false,
      mode: 'flask_capture',
      ml_engine_ready: response.data.ml_engine_ready || false,
      features_count: response.data.features_count || 0
    });
  } catch (error) {
    res.json({
      isCapturing: false,
      mode: 'idle',
      error: error.message
    });
  }
});

// Enhanced detection endpoint (forwards to Flask)
router.post('/detect', detectDDoS);

// System status
router.get('/system-status', async (req, res) => {
  try {
    const response = await require('axios').get('http://localhost:5001/health');
    res.json({
      backend_status: 'connected',
      ml_model_status: response.data.ml_engine_ready ? 'connected' : 'disconnected',
      flask_status: 'connected',
      capture_available: true,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.json({
      backend_status: 'connected',
      ml_model_status: 'disconnected',
      flask_status: 'disconnected',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;