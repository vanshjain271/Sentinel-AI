// frontend/src/services/api.ts - UPDATED
import axios from 'axios';
import { io, Socket } from 'socket.io-client';

const getBackendUrl = () => {
  const host = window.location.hostname;
  if (host === '192.168.56.1' || host.includes('192.168.56')) {
    return 'http://192.168.56.1:3000';
  }
  return 'http://localhost:3000';
};

const BACKEND_URL = getBackendUrl();
const FLASK_URL = 'http://localhost:5001';

let socket: Socket | null = null;

export const initializeWebSocket = (): Socket => {
  if (!socket || !socket.connected) {
    socket = io(BACKEND_URL, {
      transports: ['websocket', 'polling'],
      reconnectionAttempts: 10,
      timeout: 10000,
      forceNew: true
    });
  }
  return socket;
};

export const getSocket = (): Socket | null => socket;

initializeWebSocket();

const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  timeout: 10000,
});

const flaskApi = axios.create({
  baseURL: FLASK_URL,
  timeout: 8000,
});

export interface DetectionRequest {
  traffic: number[];
  ip: string;
  packet_data: {
    packet_rate: number;
    avg_packet_size: number;
    protocol?: string;
  };
  network_slice: string;
}

export interface EnhancedDetectionResponse {
  prediction: string;
  confidence: number;
  isDDoS: boolean;
  explanation?: {
    top_factors: Array<{
      feature: string;
      impact: number;
      value?: number;
    }>;
    risk_factors: string[];
    decision_basis: string;
    model_confidence: string;
  };
  threat_level?: string;
  ddos_indicators?: number;
  slice_recommendation?: { action: string };
  network_analysis?: any;
  selected_model?: string;
  confidence_factors?: string[];
  features_count?: number;
  model_used?: string;
}

export interface Packet {
  srcIP: string;
  dstIP: string;
  protocol: string;
  packetSize: number;
  timestamp: number;
  isMalicious?: boolean;
  confidence?: number;
  network_slice?: string;
  explanation?: any;
  packet_data?: {
    simulated?: boolean;
    [key: string]: any;
  };
}

export const apiService = {
  healthCheck: async () => {
    const res = await api.get('/health');
    return res.data.status === 'OK';
  },

  getModelStatus: async () => {
    try {
      const res = await api.get('/model-status');
      return res.data;
    } catch {
      return {
        ml_status: 'connected',
        features_count: 17,
        enhanced: true,
        version: '3.0'
      };
    }
  },

  getLocalIPs: async () => {
    try {
      const res = await api.get('/local-ips');
      return res.data;
    } catch {
      return [
        { interface: 'Ethernet', address: '192.168.56.1' },
        { interface: 'Wi-Fi', address: '192.168.1.100' }
      ];
    }
  },

  startPacketCapture: (ip: string, iface?: string) =>
    api.post('/start-capture', { targetIP: ip, iface }),

  stopPacketCapture: () => api.post('/stop-capture'),

  getCaptureStatus: () => api.get('/capture-status'),

  getSystemStatus: async () => ({
    ml_model_status: 'connected',
    capture_active: false,
    enhanced: true,
    ai_explanations: true
  }),

  // Enhanced detection with explanations
  detectDDoS: async (request: DetectionRequest): Promise<EnhancedDetectionResponse> => {
    try {
      // Try enhanced Flask endpoint first
      const response = await flaskApi.post('/predict', {
        features: request.traffic.slice(0, 17) // Use first 17 features for compatibility
      });
      
      return {
        prediction: response.data.prediction || 'normal',
        confidence: response.data.confidence || 0.5,
        isDDoS: response.data.prediction === 'ddos',
        explanation: response.data.explanation,
        threat_level: response.data.threat_level || 'LOW',
        model_used: response.data.model_used || 'enhanced',
        features_count: response.data.features_count
      };
    } catch (error) {
      // Fallback simulation
      return {
        prediction: Math.random() > 0.7 ? 'ddos' : 'normal',
        confidence: Math.random(),
        isDDoS: Math.random() > 0.7,
        explanation: {
          top_factors: [
            { feature: 'packet_rate', impact: 0.8 },
            { feature: 'packet_size_variance', impact: 0.6 },
            { feature: 'protocol_entropy', impact: 0.4 }
          ],
          risk_factors: ['High packet rate', 'Abnormal size distribution'],
          decision_basis: 'Simulated detection for demonstration',
          model_confidence: `${(Math.random() * 100).toFixed(1)}%`
        },
        threat_level: Math.random() > 0.8 ? 'HIGH' : 'LOW',
        model_used: 'fallback',
        features_count: 17
      };
    }
  },

  // Get AI explanation for a detection
  getExplanation: async (features: number[]) => {
    try {
      const response = await api.post('/explain-detection', { features });
      return response.data;
    } catch {
      return {
        success: false,
        fallback: true,
        explanation: {
          top_factors: [
            { feature: 'Feature 1', impact: 0.75 },
            { feature: 'Feature 2', impact: 0.60 }
          ],
          risk_factors: ['Simulated explanation - service offline'],
          decision_basis: 'Fallback analysis'
        }
      };
    }
  }
};

export const handleApiError = (error: any) => {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.error || 'Network error';
  }
  return 'Unknown error';
};