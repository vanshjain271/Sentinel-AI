export interface Packet {
  timestamp: number;
  srcIP: string;
  dstIP: string;
  protocol: string;
  network_slice?: string;
  packetSize: number;
  isMalicious?: boolean;
  detectionReason?: string;
  confidence?: number;
  explanation?: {  // NEW
    prediction: string;
    confidence: number;
    top_factors: Array<{
      feature: string;
      impact: number;
      value?: number;
    }>;
    risk_factors: string[];
    decision_basis: string;
    model_confidence?: string;
  };
  packet_data?: {
    simulated?: boolean;
    avg_packet_size?: number;
    [key: string]: any;
  };
}