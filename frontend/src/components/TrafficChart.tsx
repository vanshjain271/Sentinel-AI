import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { Activity } from 'lucide-react';

interface DataPoint {
  time: number;
  normalPps: number;
  maliciousPps: number;
  simulatedPps?: number;
}

interface Props {
  data: DataPoint[];
}

export default function TrafficChart({ data }: Props) {
  const hasMalicious = data.some((d) => d.maliciousPps > 0);

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Activity className="text-cyan-400" />
        Live Traffic
      </h3>

     
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="normalGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="maliciousGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fill: '#a0aec0', fontSize: 12 }}
              axisLine={{ stroke: '#2d3748' }}
              tickLine={{ stroke: '#2d3748' }}
              tickMargin={10}
            />
            <YAxis
              tick={{ fill: '#a0aec0', fontSize: 12 }}
              axisLine={{ stroke: '#2d3748' }}
              tickLine={{ stroke: '#2d3748' }}
              tickMargin={10}
              label={{
                value: 'Packets/s',
                angle: -90,
                position: 'insideLeft',
                fill: '#a0aec0',
                style: { textAnchor: 'middle' },
                offset: 10,
              }}
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                return (
                  <div className="bg-gray-800 p-3 border border-gray-700 rounded-lg shadow-xl">
                    <p className="text-gray-400 text-sm mb-1">Time: {label}</p>
                    {payload.map((entry, i) => (
                      <div key={i} className="flex items-center">
                        <div
                          className="w-2 h-2 rounded-full mr-2"
                          style={{ backgroundColor: entry.color ?? '#000' }}
                        />
                        <span className="text-sm">
                          {entry.name}: <span className="font-bold">{entry.value}</span>
                        </span>
                      </div>
                    ))}
                  </div>
                );
              }}
              cursor={{ stroke: '#4a5568', strokeWidth: 1 }}
            />
            <Area
              type="monotone"
              dataKey="normalPps"
              name="Normal Traffic"
              stroke="#06b6d4"
              fill="url(#normalGrad)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, strokeWidth: 2, fill: '#06b6d4' }}
              isAnimationActive
              animationDuration={1000}
              animationEasing="ease-out"
            />
            <Area
              type="monotone"
              dataKey="maliciousPps"
              name="Malicious Traffic"
              stroke="#ef4444"
              fill={hasMalicious ? 'url(#maliciousGrad)' : 'none'}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, strokeWidth: 2, fill: '#ef4444' }}
              isAnimationActive
              animationDuration={1000}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}