// backend/index.js - UPDATED for Enhanced Model System
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const axios = require('axios');
const os = require('os');
const path = require('path');

const app = express();
const server = http.createServer(app);

// ---------------- SOCKET.IO + CORS ----------------
const io = new Server(server, {
  cors: {
    origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
    methods: ["GET", "POST"],
    credentials: true
  },
  transports: ['websocket', 'polling']
});

app.set("io", io);

// ---------------- GLOBAL MIDDLEWARE ----------------
app.use(cors({
  origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));

// Protect capture control from simulated clients
app.use((req, res, next) => {
  if ((req.method === "POST") && (req.path === "/api/start-capture" || req.path === "/api/stop-capture")) {
    if (req.get("X-Simulated-Attack") === "true") {
      console.log("🔒 Ignoring simulated client request to start/stop capture");
      return res.status(200).json({ success: false, message: "Simulated clients cannot start/stop capture" });
    }
  }
  next();
});

// ---------------- CONFIG ----------------
const FLASK_URL = 'http://localhost:5001';   // Enhanced Flask system
const LAPTOP_IP = getLaptopIp();

// ---------------- STATE ----------------
let blockedIPs = [];
let maliciousPackets = [];
let isCapturing = false;
let packetCount = 0;

// ---------------- HELPERS ----------------
function getLaptopIp() {
  try {
    const ifaces = os.networkInterfaces();
    for (const iface of Object.values(ifaces)) {
      for (const info of iface) {
        if (info.family === 'IPv4' && !info.internal) {
          return info.address;
        }
      }
    }
  } catch (e) {
    // ignore
  }
  return '127.0.0.1';
}

// ---------------- HEALTH ----------------
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    ip: LAPTOP_IP, 
    time: new Date().toISOString(),
    system: 'enhanced',
    version: '3.0'
  });
});

// ---------------- CAPTURE CONTROL ----------------
app.post('/api/start-capture', async (req, res) => {
  try {
    await axios.post(`${FLASK_URL}/start-capture`);
    io.emit('capture-started');
    isCapturing = true;
    console.log("✅ Capture started via Enhanced Flask");
    res.json({ success: true, mode: 'enhanced' });
  } catch (err) {
    console.error('❌ Error starting capture:', err.message);
    res.json({ success: false, error: err.message });
  }
});

app.post('/api/stop-capture', async (req, res) => {
  try {
    await axios.post(`${FLASK_URL}/stop-capture`);
    io.emit('capture-stopped');
    isCapturing = false;
    console.log("🛑 Capture stopped via Flask");
    res.json({ success: true });
  } catch (err) {
    console.error('❌ Error stopping capture:', err.message);
    res.json({ success: false, error: err.message });
  }
});

// ---------------- LIVE PACKET STREAM ----------------
app.post('/api/live-packet', (req, res) => {
  const packet = req.body;
  packetCount++;

  // Enhanced packet handling with AI explanations
  const enhancedPacket = {
    ...packet,
    id: `pkt-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    receivedAt: new Date().toISOString()
  };

  io.emit('new_packet', enhancedPacket);

  // Log with enhanced details
  if (packet.explanation) {
    console.log(`📡 [AI] Packet from ${packet.srcIP} → Confidence: ${packet.confidence || 0}`);
  } else {
    console.log(`📡 [${packetCount}] Packet from ${packet.srcIP || 'unknown'} → ${packet.dstIP || 'unknown'}`);
  }

  res.json({ ok: true, enhanced: true });
});

// ---------------- BLOCK MANAGEMENT ----------------
app.get('/api/blocked-ips', (req, res) => {
  res.json(blockedIPs.map(ip => ({
    ...ip,
    system: 'enhanced',
    hasExplanation: !!ip.explanation
  })));
});

app.post('/api/emit-blocked-ip', (req, res) => {
  const { 
    ip, 
    confidence = 99, 
    reason = 'DDoS Flood',
    explanation = null,
    model_used = 'enhanced',
    network_slice = 'eMBB'
  } = req.body;
  
  if (!ip) return res.status(400).json({ error: 'No IP provided' });

  const block = {
    ip,
    timestamp: new Date().toISOString(),
    reason,
    threatLevel: confidence > 90 ? 'high' : confidence > 70 ? 'medium' : 'low',
    mitigation: 'SDN DROP Rule',
    confidence,
    explanation,
    model_used,
    network_slice,
    features_count: explanation?.features_count || 0
  };

  if (!blockedIPs.find(b => b.ip === ip)) {
    blockedIPs.push(block);
    maliciousPackets.push({
      id: Date.now(),
      timestamp: Date.now(),
      srcIP: ip,
      dstIP: LAPTOP_IP,
      protocol: 'UDP',
      packetSize: 1024,
      action: 'Blocked',
      prediction: 'ddos',
      confidence,
      explanation
    });
  }

  io.emit('ip_blocked', block);
  io.emit('update_blocked_ips', blockedIPs);
  io.emit('detection-result', {
    ip,
    is_ddos: true,
    confidence: confidence / 100,
    prediction: 'ddos',
    abuseScore: confidence,
    threat_level: confidence > 90 ? 'HIGH' : confidence > 70 ? 'MEDIUM' : 'LOW',
    explanation,
    model_used
  });

  console.log(`🚫 Enhanced Blocked IP: ${ip} (Confidence: ${confidence}%)`);

  res.json({ success: true, enhanced: true });
});

app.post('/api/unblock', (req, res) => {
  const { ip } = req.body;
  blockedIPs = blockedIPs.filter(b => b.ip !== ip);
  io.emit('update_blocked_ips', blockedIPs);
  io.emit('unblocked_ip', { ip });
  console.log(`♻️ Unblocked IP: ${ip}`);
  res.json({ success: true });
});

// ---------------- ENHANCED MODEL STATUS ----------------
app.get('/api/model-status', async (req, res) => {
  try {
    const response = await axios.get(`${FLASK_URL}/health`, { timeout: 3000 });
    res.json({
      ml_status: response.data.ml_engine_ready ? 'connected' : 'disconnected',
      features_count: response.data.features_count || 0,
      version: response.data.version || 'unknown',
      enhanced: true,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.json({
      ml_status: 'disconnected',
      error: error.message,
      enhanced: false,
      timestamp: new Date().toISOString()
    });
  }
});

// ---------------- AI EXPLANATION ENDPOINT ----------------
app.post('/api/explain-detection', async (req, res) => {
  try {
    const { features } = req.body;
    
    // Forward to Flask for AI explanation
    const response = await axios.post(`${FLASK_URL}/predict`, {
      features
    }, { timeout: 5000 });
    
    res.json({
      success: true,
      explanation: response.data.explanation,
      prediction: response.data.prediction,
      confidence: response.data.confidence
    });
  } catch (error) {
    console.error('Explanation error:', error.message);
    res.json({
      success: false,
      error: 'Explanation service unavailable',
      fallback: true
    });
  }
});

// ---------------- SOCKET EVENTS ----------------
io.on('connection', (socket) => {
  console.log('⚡ Frontend CONNECTED:', socket.id);

  socket.emit('initial_blocked_ips', blockedIPs);
  socket.emit('capture-status', {
    isCapturing,
    packetCount,
    packetsPerSecond: 0,
    totalBytes: 0,
    duration: 0,
    system: 'enhanced'
  });

  socket.emit('system-info', {
    version: '3.0',
    enhanced: true,
    ai_capable: true,
    model_status: 'ready',
    features: ['ai_explanations', '5g_slicing', 'real_time_ml']
  });

  socket.on('disconnect', () => {
    console.log('❎ Frontend disconnected');
  });
});

// ---------------- SERVER START ----------------
const PORT = 3000;
server.listen(PORT, '0.0.0.0', () => {
  console.log('\n🚀 SentinelAI Enhanced Backend LIVE');
  console.log(`🌐 http://localhost:${PORT}`);
  console.log(`🤖 ML Engine: http://localhost:5001`);
  console.log(`🩺 Health: http://localhost:${PORT}/api/health`);
  console.log(`🧠 Model Status: http://localhost:${PORT}/api/model-status\n`);
});