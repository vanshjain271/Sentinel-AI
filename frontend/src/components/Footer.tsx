import React from 'react';

interface Props {
  connected: boolean;
}

export default function Footer({ connected }: Props) {
  return (
    <div className="text-center text-gray-500 text-sm mt-10">
      <p>Real-time DDoS Detection • Ryu SDN Mitigation • AI-Powered</p>
      <p className="mt-2">{connected ? 'All systems operational' : 'Waiting for backend...'}</p>
    </div>
  );
}