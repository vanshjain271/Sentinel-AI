import React from 'react';
import { Packet } from '../types';
import { AlertTriangle, Shield, Info, Brain } from 'lucide-react';

const PROTOCOL_COLORS: Record<string, string> = {
  TCP: 'bg-emerald-600 text-white',
  UDP: 'bg-blue-600 text-white',
  ICMP: 'bg-yellow-600 text-white',
  IGMP: 'bg-orange-600 text-white',
  OSPF: 'bg-purple-600 text-white',
  ESP: 'bg-red-600 text-white',
  AH: 'bg-pink-600 text-white',
  IPv6: 'bg-indigo-600 text-white',
  default: 'bg-gray-600 text-white',
};

const getProtocolColor = (protocol: string) => {
  return PROTOCOL_COLORS[protocol.toUpperCase()] || PROTOCOL_COLORS.default;
};

const formatISTTime = (timestamp: number) => {
  const date = new Date(timestamp);
  const istOffset = 5.5 * 60 * 60 * 1000;
  const istTime = new Date(date.getTime() + istOffset);

  return istTime.toLocaleTimeString('en-US', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  });
};

interface LivePacketTableProps {
  packets: Packet[];
  capturing: boolean;
  onPacketSelect?: (packet: Packet) => void;
}

export default function LivePacketTable({ packets, capturing, onPacketSelect }: LivePacketTableProps) {
  if (packets.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8 bg-gray-900/50 rounded-xl">
        {capturing ? (
          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="animate-pulse">
              <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p className="text-sm">Capturing network traffic...</p>
          </div>
        ) : (
          <p className="text-sm">Start capture to see live packets</p>
        )}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto max-h-96">
      <table className="min-w-full text-sm font-mono border-collapse bg-gray-800 rounded-xl shadow-lg overflow-hidden">
        <thead>
          <tr className="bg-gradient-to-r from-cyan-600 to-purple-700 sticky top-0 text-white">
            <th className="px-4 py-3 text-left font-semibold">Time</th>
            <th className="px-4 py-3 text-left font-semibold">Source</th>
            <th className="px-4 py-3 text-left font-semibold">Destination</th>
            <th className="px-4 py-3 text-left font-semibold">Protocol</th>
            <th className="px-4 py-3 text-left font-semibold">Slice</th>
            <th className="px-4 py-3 text-left font-semibold">Size</th>
            <th className="px-4 py-3 text-left font-semibold">Detection</th>
            <th className="px-4 py-3 text-left font-semibold">AI</th>
          </tr>
        </thead>
        <tbody>
          {packets.map((p, idx) => {
            const isSimulated = p.packet_data?.simulated === true;
            const isMalicious = p.isMalicious === true;
            const protoColor = getProtocolColor(p.protocol);
            const hasExplanation = !!p.explanation;

            return (
              <tr
                key={idx}
                className={`transition-all duration-200 border-b cursor-pointer hover:bg-gray-700/50 ${
                  isMalicious
                    ? isSimulated
                      ? 'bg-purple-900/20 hover:bg-purple-900/30 border-l-4 border-l-purple-500'
                      : 'bg-red-900/20 hover:bg-red-900/30 border-l-4 border-l-red-500'
                    : 'border-gray-700 hover:bg-cyan-900/10'
                }`}
                onClick={() => onPacketSelect && onPacketSelect(p)}
              >
                <td className="px-4 py-2 text-gray-300 text-xs font-medium">
                  {formatISTTime(p.timestamp)}
                </td>
                <td className="px-4 py-2">
                  <div className="flex items-center gap-1.5">
                    {isMalicious && isSimulated && (
                      <Shield className="w-3.5 h-3.5 text-purple-400" />
                    )}
                    {isMalicious && !isSimulated && (
                      <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
                    )}
                    <span
                      className={`font-mono text-sm ${
                        isMalicious
                          ? isSimulated
                            ? 'text-purple-300'
                            : 'text-red-300'
                          : 'text-orange-300'
                      }`}
                    >
                      {p.srcIP}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-2 text-purple-300 font-mono text-sm">
                  {p.dstIP}
                </td>
                <td className="px-4 py-2">
                  <span
                    className={`px-2.5 py-1 rounded font-bold text-xs tracking-wider ${protoColor}`}
                  >
                    {p.protocol}
                  </span>
                </td>
                <td className="px-4 py-2">
                  <span
                    className={`px-2 py-1 rounded text-white text-xs font-medium ${
                      p.network_slice === 'eMBB'
                        ? 'bg-purple-700/80'
                        : p.network_slice === 'URLLC'
                        ? 'bg-blue-600/80'
                        : 'bg-green-600/80'
                    }`}
                  >
                    {p.network_slice || 'eMBB'}
                  </span>
                </td>
                <td className="px-4 py-2 text-gray-200 font-mono text-sm">
                  {p.packetSize}B
                </td>
                <td className="px-4 py-2">
                  {isMalicious ? (
                    <div className="flex items-center gap-1.5">
                      <span
                        className={`px-2.5 py-1 rounded text-white text-xs font-bold flex items-center gap-1.5 ${
                          isSimulated
                            ? 'bg-purple-600/90'
                            : 'bg-red-500/90'
                        }`}
                      >
                        {isSimulated ? (
                          <Shield className="w-3.5 h-3.5" />
                        ) : (
                          <AlertTriangle className="w-3.5 h-3.5" />
                        )}
                        Malicious
                        {p.confidence !== undefined && (
                          <span className="ml-1 opacity-90">
                            ({(p.confidence * 100).toFixed(0)}%)
                          </span>
                        )}
                      </span>
                    </div>
                  ) : (
                    <span className="px-2.5 py-1 bg-green-500/80 rounded text-white text-xs font-bold">
                      Normal
                      {p.confidence !== undefined && (
                        <span className="ml-1 opacity-80">
                          ({((1 - p.confidence) * 100).toFixed(0)}%)
                        </span>
                      )}
                    </span>
                  )}
                </td>
                <td className="px-4 py-2">
                  {hasExplanation ? (
                    <button
                      className="p-1.5 rounded bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all"
                      title="View AI Explanation"
                      onClick={(e) => {
                        e.stopPropagation();
                        onPacketSelect && onPacketSelect(p);
                      }}
                    >
                      <Info className="w-3.5 h-3.5 text-white" />
                    </button>
                  ) : isMalicious ? (
                    <button
                      className="p-1.5 rounded bg-gray-700 hover:bg-gray-600 transition-colors"
                      title="Generate AI Analysis"
                      onClick={(e) => {
                        e.stopPropagation();
                        onPacketSelect && onPacketSelect(p);
                      }}
                    >
                      <Brain className="w-3.5 h-3.5 text-gray-400" />
                    </button>
                  ) : (
                    <span className="text-gray-500 text-xs">—</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}