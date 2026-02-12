import React from 'react';
import { Shield } from 'lucide-react';
import clsx from 'clsx';

interface Props {
  capturing: boolean;
  onToggle: () => void;
}

export default function ControlButton({ capturing, onToggle }: Props) {
  return (
    <button
      onClick={onToggle}
      className={clsx(
        'px-8 py-4 md:py-6 rounded-2xl text-xl md:text-2xl font-extrabold transition-transform transform hover:scale-105 shadow-2xl flex items-center gap-2 h-fit',
        capturing
          ? 'bg-red-600 hover:bg-red-700 text-white border-2 border-red-300'
          : 'bg-blue-600 hover:bg-blue-700 text-white border-2 border-blue-300'
      )}
    >
      <Shield className="w-6 h-6 md:w-8 md:h-8" />
      {capturing ? 'STOP CAPTURE' : 'START CAPTURE'}
    </button>
  );
}