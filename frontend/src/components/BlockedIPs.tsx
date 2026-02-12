import React from "react";
import { Shield, Unlock, Brain } from "lucide-react";

type ThreatLevel = "high" | "medium" | "low" | "simulated";

interface BlockedIP {
  ip?: string;
  timestamp?: string;
  reason?: string;
  threatLevel?: ThreatLevel;
  mitigation?: string;
  isSimulated?: boolean;
  confidence?: number;
  explanation?: any; // NEW
  model_used?: string; // NEW
  network_slice?: string; // NEW
}

interface BlockedIPsProps {
  blockedIPs?: BlockedIP[];
  onExplain?: (ipData: BlockedIP) => void; // NEW
}

export default function BlockedIPs({ blockedIPs = [], onExplain }: BlockedIPsProps) {
  const list = Array.isArray(blockedIPs) ? blockedIPs : [];

  const unblock = async (ip?: string) => {
    if (!ip) return;
    try {
      await fetch("http://localhost:3000/api/unblock", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip }),
      });
    } catch (err) {
      console.error("Unblock error:", err);
    }
  };

  const formatTime = (ts?: string) => {
    try {
      if (!ts) return "";
      const d = new Date(ts);
      if (isNaN(d.getTime())) return ts;
      return d.toLocaleTimeString();
    } catch {
      return ts || "";
    }
  };

  const renderThreatBadge = (level?: ThreatLevel, isSimulated?: boolean) => {
    if (isSimulated) {
      return (
        <span className="px-2 py-1 rounded text-xs font-bold bg-purple-600 text-white flex items-center gap-1">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10a1 1 0 01-1.64 0l-7-10A1 1 0 014 7h4V2a1 1 0 01.7-.954l2.6-.866z" clipRule="evenodd" />
          </svg>
          SIMULATED
        </span>
      );
    }
    
    const lvl: ThreatLevel = level || "low";
    const className =
      lvl === "high" 
        ? "bg-red-600 text-white" 
        : lvl === "medium" 
          ? "bg-orange-500 text-white" 
          : "bg-yellow-600 text-black";
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold ${className}`}>
        {lvl.toUpperCase()}
      </span>
    );
  };

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
      <div className="p-4 bg-gradient-to-r from-red-900/50 to-purple-900/50 border-b border-gray-800">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-bold flex items-center gap-2">
            <Shield className="w-5 h-5 text-red-400" />
            Blocked Attackers ({list.length})
          </h3>
          {list.some(ip => ip.explanation) && (
            <span className="text-sm text-gray-300 flex items-center gap-1">
              <Brain className="w-4 h-4" />
              AI Analysis Available
            </span>
          )}
        </div>
      </div>

      {list.length === 0 ? (
        <div className="p-12 text-center">
          <Shield className="w-16 h-16 mx-auto mb-4 text-gray-700" />
          <p className="text-gray-400">No threats blocked</p>
          <p className="text-sm text-gray-500 mt-2">System is secure</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs text-gray-500 border-b border-gray-800">
                <th className="px-4 py-3">IP Address</th>
                <th className="px-4 py-3">Threat</th>
                <th className="px-4 py-3">Reason</th>
                <th className="px-4 py-3">Slice</th>
                <th className="px-4 py-3">AI</th>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {list.map((item, idx) => {
                const ip = item && typeof item.ip === "string" && item.ip.length > 0 ? item.ip : `unknown-${idx}`;
                const threat = item && (item.threatLevel as ThreatLevel);
                const reason = item && item.reason ? item.reason : "DDoS Flood";
                const time = formatTime(item && item.timestamp);
                const hasExplanation = !!item.explanation;
                const confidence = item.confidence || 0;

                return (
                  <tr
                    key={ip + "-" + idx}
                    className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-red-400 text-sm">{ip}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-col gap-1">
                        {renderThreatBadge(threat)}
                        {confidence > 0 && (
                          <span className="text-xs text-gray-400">
                            {Math.round(confidence * 100)}% confidence
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-300 text-sm max-w-xs truncate" title={reason}>
                      {reason}
                    </td>
                    <td className="px-4 py-3">
                      {item.network_slice ? (
                        <span className={`px-2 py-1 rounded text-xs ${
                          item.network_slice === 'URLLC' ? 'bg-blue-900/50 text-blue-300' :
                          item.network_slice === 'mMTC' ? 'bg-green-900/50 text-green-300' :
                          'bg-purple-900/50 text-purple-300'
                        }`}>
                          {item.network_slice}
                        </span>
                      ) : (
                        <span className="text-gray-500 text-xs">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {hasExplanation ? (
                        <button
                          onClick={() => onExplain && onExplain(item)}
                          className="flex items-center gap-1 px-3 py-1.5 rounded text-xs bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all"
                          title="View AI Analysis"
                        >
                          <Brain className="w-3 h-3" />
                          Explain
                        </button>
                      ) : (
                        <span className="text-gray-500 text-xs">No AI</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{time}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => unblock(ip)}
                          disabled={item.isSimulated}
                          className={`flex items-center gap-1 px-3 py-1.5 rounded text-xs transition-colors ${
                            item.isSimulated 
                              ? 'bg-gray-700 text-gray-400 cursor-not-allowed' 
                              : 'bg-blue-600 hover:bg-blue-700'
                          }`}
                          title={item.isSimulated ? 'Simulated attacks cannot be unblocked' : 'Unblock IP'}
                        >
                          <Unlock className="w-3 h-3" />
                          {item.isSimulated ? 'Simulated' : 'Unblock'}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}