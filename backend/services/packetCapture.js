// packetCapture.js - UPDATED to work with Flask
const { spawn } = require('child_process');
const EventEmitter = require('events');
const axios = require('axios');

class PacketCapture extends EventEmitter {
  constructor() {
    super();
    this.isCapturing = false;
    this.tsharkProcess = null;
    this.flowWindow = [];
    this.windowDuration = 60000;
    this.tsharkPath = 'C:\\Program Files\\Wireshark\\tshark.exe';
    this.flaskEndpoint = 'http://localhost:5001/process-packet'; // Updated
  }

  startCapture(targetIP, interfaceName) {
    if (this.isCapturing) return;
    
    this.isCapturing = true;
    this.flowWindow = [];
    this.captureStartTime = Date.now();
    
    const args = [
      '-i', interfaceName,
      '-f', `host ${targetIP}`,
      '-l',
      '-T', 'fields',
      '-e', 'frame.time_epoch',
      '-e', 'ip.src',
      '-e', 'ip.dst',
      '-e', '_ws.col.Protocol',
      '-e', 'frame.len'
    ];
    
    console.log(`Starting tshark capture on ${interfaceName} for ${targetIP}`);
    
    try {
      this.tsharkProcess = spawn(this.tsharkPath, args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: true
      });
      
      this.tsharkProcess.stdout.on('data', (data) => {
        const lines = data.toString().split('\n');
        lines.forEach(line => {
          if (line.trim()) {
            this.processPacketLine(line.trim(), targetIP);
          }
        });
      });
      
      this.tsharkProcess.stderr.on('data', (data) => {
        const errorMsg = data.toString();
        console.error('tshark stderr:', errorMsg);
        if (errorMsg.includes('No such device')) {
          this.emit('error', new Error('Interface access error'));
          this.stopCapture();
        }
      });
      
      this.tsharkProcess.on('close', (code) => {
        console.log(`tshark process exited with code ${code}`);
        this.isCapturing = false;
      });
      
    } catch (error) {
      console.error('Failed to start tshark:', error);
      this.emit('error', error);
      this.isCapturing = false;
    }
  }

  async processPacketLine(line, targetIP) {
    const fields = line.split('\t').map(f => f.trim());
    
    if (fields.length < 4) {
      return;
    }
    
    const packet = {
      timestamp: parseFloat(fields[0]) * 1000,
      src_ip: fields[1],
      dst_ip: fields[2],
      protocol: fields[3].toUpperCase(),
      size: parseInt(fields[4]) || 0
    };
    
    // Add to flow window
    this.flowWindow.push(packet);
    
    // Clean old packets
    const now = Date.now();
    this.flowWindow = this.flowWindow.filter(p => now - p.timestamp < this.windowDuration);
    
    // Send to Flask for analysis
    try {
      await axios.post(this.flaskEndpoint, { packet }, { timeout: 100 });
    } catch (error) {
      // Silent fail - Flask might be busy
    }
    
    this.emit('packet', packet);
  }

  stopCapture() {
    this.isCapturing = false;
    
    if (this.tsharkProcess) {
      this.tsharkProcess.kill('SIGTERM');
      setTimeout(() => {
        if (this.tsharkProcess && !this.tsharkProcess.killed) {
          this.tsharkProcess.kill('SIGKILL');
        }
      }, 3000);
      
      this.tsharkProcess = null;
    }
    
    this.flowWindow = [];
    console.log('Packet capture stopped');
    this.emit('capture_stopped');
  }

  getFlowWindow() {
    return this.flowWindow;
  }
}

module.exports = PacketCapture;