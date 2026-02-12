import React from 'react';
import { Wifi, WifiOff, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';

interface Props {
  connected: boolean;
  error?: string;
}

export default function ConnectionStatus({ connected, error }: Props) {
  return (
    <>
      <div
        className={clsx(
          'px-6 py-3 rounded-full flex items-center gap-2 text-lg font-bold shadow-lg transition-all border-2',
          connected
            ? 'bg-green-500/20 text-green-400 border-green-500/70'
            : 'bg-red-500/20 text-red-400 border-red-500/70'
        )}
      >
        {connected ? <Wifi className="w-6 h-6" /> : <WifiOff className="w-6 h-6" />}
        <span className="hidden sm:inline">{connected ? 'LIVE' : 'OFFLINE'}</span>
      </div>

      {error && (
        <div className="mt-6 p-4 bg-red-900/50 border border-red-700 rounded-xl flex items-center gap-3 animate-pulse">
          <AlertTriangle className="w-6 h-6" />
          <span>{error}</span>
        </div>
      )}
    </>
  );
}