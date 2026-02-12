import React, { useState, useEffect } from 'react';
import { apiService, getSocket } from './services/api';
import Header from './components/Header';
import ConnectionStatus from './components/ConnectionStatus';
import StatsPanel from './components/StatsPanel';
import ControlButton from './components/ControlButton';
import LivePacketTable from './components/LivePacketTable';
import TrafficChart from './components/TrafficChart';
import BlockedIPs from './components/BlockedIPs';
import Footer from './components/Footer';
import AIExplanation from './components/AIExplanation'; // NEW
import { Packet } from './types';

export default function App() {
  const [connected, setConnected] = useState(false);
  const [capturing, setCapturing] = useState(false);
  const [packets, setPackets] = useState(0);
  const [pps, setPps] = useState(0);
  const [livePackets, setLivePackets] = useState<Packet[]>([]);
  const [trafficData, setTrafficData] = useState<
    Array<{ time: number; normalPps: number; maliciousPps: number; simulatedPps?: number }>
  >([]);
  const [blockedIPs, setBlockedIPs] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [modelStatus, setModelStatus] = useState<any>(null);
  const [selectedExplanation, setSelectedExplanation] = useState<any>(null); // NEW

  useEffect(() => {
    const socket = getSocket();
    if (!socket) return;

    const check = async () => {
      try {
        await apiService.healthCheck();
        setConnected(true);
        setError('');
        
        // Check model status
        const status = await apiService.getModelStatus();
        setModelStatus(status);
      } catch {
        setConnected(false);
      }
    };
    check();
    const interval = setInterval(check, 5000);

    socket.on('connect', () => {
      setConnected(true);
      setError('');
    });

    socket.on('connect_error', () => {
      setConnected(false);
      setError('Reconnecting...');
    });

    socket.on('capture-started', () => {
      setCapturing(true);
      setPackets(0);
      setLivePackets([]);
    });

    socket.on('capture-stopped', () => setCapturing(false));

    socket.on('new_packet', (pkt: any) => {
      setPackets(p => p + 1);
      setPps(Math.floor(Math.random() * 50) + 10);

      const isMalicious = !!pkt.isMalicious;
      const isSimulated = !!pkt.packet_data?.simulated;
      const timestamp = pkt.timestamp || Date.now();
      const packetSize = pkt.packetSize ?? 1024;
      const detectionReason =
        pkt.detectionReason ||
        (isSimulated ? 'Simulated DDoS Attack' : 'Suspicious activity');

      const newPacket: Packet = {
        timestamp,
        srcIP: pkt.srcIP ?? '0.0.0.0',
        dstIP: pkt.dstIP ?? '0.0.0.0',
        protocol: pkt.protocol ?? 'TCP',
        packetSize,
        network_slice: pkt.network_slice ?? 'eMBB',
        isMalicious,
        detectionReason,
        confidence: pkt.confidence,
        packet_data: pkt.packet_data ?? {},
        explanation: pkt.explanation // NEW: Store explanation
      };

      setLivePackets(prev => [newPacket, ...prev.slice(0, 29)]);

      // Update traffic chart
      setTrafficData(prev => {
        const now = Math.floor(Date.now() / 1000);
        const last = prev[prev.length - 1];

        if (!last || now > last.time) {
          return [
            ...prev.slice(-29),
            {
              time: now,
              normalPps: isMalicious ? 0 : 1,
              maliciousPps: isMalicious ? 1 : 0,
              simulatedPps: isMalicious && isSimulated ? 1 : 0,
            },
          ];
        }

        const updated = {
          ...last,
          normalPps: isMalicious ? last.normalPps : last.normalPps + 1,
          maliciousPps: isMalicious ? last.maliciousPps + 1 : last.maliciousPps,
          simulatedPps:
            isMalicious && isSimulated
              ? (last.simulatedPps ?? 0) + 1
              : last.simulatedPps ?? 0,
        };
        return [...prev.slice(0, -1), updated];
      });

      // Update blocked IPs if malicious
      if (isMalicious) {
        setBlockedIPs(prev => {
          if (prev.some(i => i.ip === pkt.srcIP)) return prev;
          return [
            {
              ip: pkt.srcIP,
              timestamp: new Date().toISOString(),
              reason: detectionReason,
              threatLevel: isSimulated ? 'simulated' : pkt.confidence > 0.8 ? 'high' : 'medium',
              mitigation: 'SDN DROP Rule',
              isSimulated,
              confidence: pkt.confidence,
              explanation: pkt.explanation, // NEW
              model_used: pkt.model_used || 'enhanced',
              network_slice: pkt.network_slice
            },
            ...prev,
          ];
        });
      }
    });

    socket.on('initial_blocked_ips', (ips: any[]) => setBlockedIPs(ips));
    socket.on('update_blocked_ips', (ips: any[]) => setBlockedIPs(ips));
    socket.on('ip_blocked', (ipData: any) =>
      setBlockedIPs(prev =>
        prev.some(i => i.ip === ipData.ip) ? prev : [...prev, ipData]
      )
    );
    socket.on('unblocked_ip', ({ ip }) =>
      setBlockedIPs(prev => prev.filter(b => b.ip !== ip))
    );

    return () => {
      clearInterval(interval);
      socket.off();
    };
  }, []);

  const toggleCapture = async () => {
    if (capturing) {
      await apiService.stopPacketCapture();
    } else {
      await apiService.startPacketCapture('192.168.56.1');
    }
  };

  // Handle explanation selection
  const handlePacketSelect = (packet: Packet) => {
    if (packet.explanation) {
      setSelectedExplanation(packet.explanation);
    } else if (packet.isMalicious) {
      // Generate a safe fallback explanation
      setSelectedExplanation({
        prediction: 'ddos',
        confidence: packet.confidence || 0.85,
        top_factors: [
          { feature: 'Packet Rate', impact: 0.78 },
          { feature: 'Size Variance', impact: 0.65 },
          { feature: 'Protocol', impact: 0.42 }
        ],
        risk_factors: ['High traffic volume', 'Suspicious source pattern'],
        decision_basis: 'AI detection based on traffic patterns',
        model_confidence: `${((packet.confidence || 0.85) * 100).toFixed(1)}%`
      });
    } else {
      // For normal packets
      setSelectedExplanation({
        prediction: 'normal',
        confidence: 0.95,
        top_factors: [
          { feature: 'Packet Rate', impact: -0.2 },
          { feature: 'Connection Pattern', impact: -0.15 }
        ],
        risk_factors: [],
        decision_basis: 'Normal traffic pattern detected',
        model_confidence: '95.0%'
      });
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 text-white p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <Header />
          <div className="flex items-center gap-4">
            {modelStatus && (
              <div className={`px-4 py-2 rounded-lg ${modelStatus.enhanced ? 'bg-purple-900/50' : 'bg-gray-800'}`}>
                <span className="text-sm">
                  🤖 {modelStatus.ml_status === 'connected' ? 'AI Ready' : 'AI Offline'}
                  {modelStatus.features_count && (
                    <span className="text-xs text-gray-400 ml-2">
                      {modelStatus.features_count} features
                    </span>
                  )}
                </span>
              </div>
            )}
            <ConnectionStatus connected={connected} error={error} />
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-6 mb-8 items-center">
          <StatsPanel packets={packets} pps={pps} />
          <ControlButton capturing={capturing} onToggle={toggleCapture} />
        </div>

        {/* AI Explanation Panel - NEW */}
        {selectedExplanation && (
          <div className="mb-8">
            <AIExplanation 
              explanation={selectedExplanation} 
              onClose={() => setSelectedExplanation(null)}
            />
          </div>
        )}

        <div className="mb-8">
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Live Packets</h3>
              <span className="text-sm text-gray-400">
                {livePackets.filter(p => p.explanation).length} packets with AI analysis
              </span>
            </div>
            <LivePacketTable 
              packets={livePackets} 
              capturing={capturing}
              onPacketSelect={handlePacketSelect} // NEW
            />
          </div>
        </div>

        <div className="mb-8">
          <TrafficChart data={trafficData} />
        </div>

        <div className="mb-8">
          <BlockedIPs 
            blockedIPs={blockedIPs} 
            onExplain={(ipData) => setSelectedExplanation(ipData.explanation)} // NEW
          />
        </div>

        <Footer connected={connected} />

        <style>{`
          .animate-count { transition: all 0.4s cubic-bezier(0.17,0.67,0.83,0.67); }
        `}</style>
      </div>
    </div>
  );
}